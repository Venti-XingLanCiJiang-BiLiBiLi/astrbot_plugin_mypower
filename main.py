import os
import random
import asyncio
import time
import tempfile
from PIL import Image

from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger, AstrBotConfig
import astrbot.api.message_components as Comp


@register(
    "astrbot_plugin_mypower",
    "TianYi",
    "一款随机生成超能力的插件（适用于OneBot V11）",
    "1.1.0",
)
class MyPowerPlugin(Star):
    """随机生成超能力插件 - 从四个素材文件夹各选一张图拼接成超能力卡片"""

    # 冷却时间（秒）
    CD_SECONDS = 300

    def __init__(self, context: Context, config: AstrBotConfig = None):
        super().__init__(context)
        self.plugin_dir = os.path.dirname(os.path.abspath(__file__))
        self.pillow_available = True

        # 读取插件配置
        if config is None:
            config = AstrBotConfig()
        self.config = config
        self.trigger_keywords = self.config.get(
            "trigger_keyword", ["我的超能力"]
        )
        self.material_folders = self.config.get(
            "material_folders", ["超能力", "但是", "主义", "万圣节"]
        )
        self.admin_uids = self.config.get("admin_uids", [])

        # 冷却记录: {user_id: last_timestamp}
        self._last_use_time: dict[str, float] = {}

        logger.info(
            f"插件配置加载完成: trigger_keywords={self.trigger_keywords}, "
            f"material_folders={self.material_folders}, "
            f"admin_uids={self.admin_uids}"
        )

    async def initialize(self):
        """检查 Pillow 是否可用"""
        try:
            from PIL import Image as _test_img

            _test_img.new("RGB", (1, 1))
            self.pillow_available = True
        except ImportError:
            self.pillow_available = False
            logger.error(
                "Pillow 库未安装，请执行: pip install pillow"
            )

    def _create_image(self, selected_images: list) -> Image.Image:
        """将多张图片垂直拼接成一张长图

        Args:
            selected_images: 图片路径列表

        Returns:
            拼接后的 PIL Image 对象
        """
        # 读取第一张图片以确定宽度
        first_image = Image.open(selected_images[0])
        total_width = first_image.width

        # 计算总高度并统一宽度
        total_height = 0
        images_to_join = []
        for img_path in selected_images:
            img = Image.open(img_path)
            if img.width != total_width:
                new_height = int(total_width * img.height / img.width)
                img = img.resize((total_width, new_height), Image.Resampling.LANCZOS)
            total_height += img.height
            images_to_join.append(img)

        # 创建新画布并逐张拼接
        new_image = Image.new("RGB", (total_width, total_height), (255, 255, 255))
        current_height = 0
        for img in images_to_join:
            new_image.paste(img, (0, current_height))
            current_height += img.height

        return new_image

    @filter.regex(r"^.+$")
    async def my_superpower(self, event: AstrMessageEvent):
        """处理唤醒词指令，随机生成超能力图片

        从配置的素材文件夹列表中各随机选一张图，按顺序拼接后发送。
        受冷却时间（5分钟）限制，管理员不受此限制。
        """
        # 检查消息是否匹配配置的唤醒词列表
        message_text = event.message_str.strip()
        if message_text not in self.trigger_keywords:
            return

        sender_id = event.get_sender_id()
        if not sender_id:
            return

        # 冷却检查（管理员豁免）
        now = time.time()
        is_admin = sender_id in self.admin_uids or event.is_admin()
        if not is_admin:
            last_time = self._last_use_time.get(sender_id, 0)
            elapsed = now - last_time
            if elapsed < self.CD_SECONDS:
                remain = int(self.CD_SECONDS - elapsed)
                yield event.plain_result(
                    f"冷却中，请 {remain} 秒后再试 ⏳"
                )
                return

        if not self.pillow_available:
            yield event.plain_result("图片处理功能无法使用，因为 Pillow 库没有安装。")
            return

        folders = self.material_folders
        selected_images = []

        # 从各素材文件夹中依次随机选择图片
        for folder in folders:
            folder_path = os.path.join(self.plugin_dir, folder)
            if not os.path.isdir(folder_path):
                logger.warning(f"素材文件夹不存在: {folder_path}")
                continue

            images = [
                os.path.join(folder_path, f)
                for f in os.listdir(folder_path)
                if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif"))
            ]
            if images:
                selected_images.append(random.choice(images))
            else:
                yield event.plain_result(f"「{folder}」文件夹中未找到图片素材。")
                return

        if len(selected_images) < len(folders):
            yield event.plain_result("图片素材不足，无法生成超能力。请检查素材文件夹。")
            return

        try:
            # 合成图片
            new_image = self._create_image(selected_images)

            # 保存到临时文件，发送后清理
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                temp_path = tmp.name
                new_image.save(temp_path, format="PNG")

            # 记录本次使用时间（非管理员）
            if not is_admin:
                self._last_use_time[sender_id] = now

            # 发送图片
            yield event.image_result(temp_path)

            # 30秒后清理临时文件
            async def _cleanup():
                await asyncio.sleep(30)
                try:
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
                        logger.debug(f"已清理临时文件: {temp_path}")
                except Exception as e:
                    logger.warning(f"清理临时文件失败: {e}")

            asyncio.create_task(_cleanup())

        except Exception as e:
            logger.error(f"生成超能力图片失败: {e}")
            yield event.plain_result(f"图片生成失败: {e}")
