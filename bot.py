# =============================================
#   GRABZILLA BOT — bot.py
#   Developer: @khojiakbar_khaydaraliyev
# =============================================

import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import BOT_TOKEN, ADMIN_IDS, REQUIRED_CHANNEL
from languages import t
from database import init_db, add_user, get_user_lang, set_user_lang, log_download, get_stats
from downloader import detect_platform, download_video, cleanup_file

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot va Dispatcher
bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(storage=MemoryStorage())


# ─── FSM States ────────────────────────────────────────────────
class DownloadStates(StatesGroup):
    waiting_quality = State()


# ─── Yordamchi funksiyalar ──────────────────────────────────────
def lang_keyboard():
    """Til tanlash klaviaturasi"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="lang_uz"),
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
        ]
    ])


def quality_keyboard(lang: str):
    """YouTube sifat tanlash klaviaturasi"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t(lang, "q_360"), callback_data="q_360"),
            InlineKeyboardButton(text=t(lang, "q_720"), callback_data="q_720"),
        ],
        [
            InlineKeyboardButton(text=t(lang, "q_1080"), callback_data="q_1080"),
            InlineKeyboardButton(text=t(lang, "q_mp3"), callback_data="q_mp3"),
        ],
        [
            InlineKeyboardButton(text=t(lang, "back"), callback_data="q_cancel"),
        ]
    ])


def subscribe_keyboard(lang: str):
    """Obuna klaviaturasi"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "subscribe_btn"), url=f"https://t.me/{REQUIRED_CHANNEL.lstrip('@')}")],
        [InlineKeyboardButton(text=t(lang, "check_btn"), callback_data="check_sub")],
    ])


async def check_subscription(user_id: int) -> bool:
    """Obunani tekshirish"""
    if not REQUIRED_CHANNEL:
        return True
    try:
        member = await bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        return member.status not in ["left", "kicked", "banned"]
    except Exception:
        return True


async def do_download(message: types.Message, url: str, quality: str = None, lang: str = "uz"):
    """Yuklab olish va yuborish"""
    user_id = message.from_user.id
    platform = detect_platform(url)

    msg = await message.answer(t(lang, "downloading"))

    result = await asyncio.get_event_loop().run_in_executor(
        None, download_video, url, quality
    )

    await msg.delete()

    if not result["success"]:
        err = result.get("error", "")
        if "too_large" in err or err == "too_large":
            await message.answer(t(lang, "too_large"))
        elif err == "unsupported":
            await message.answer(t(lang, "unsupported"))
        else:
            await message.answer(t(lang, "error"))
        logger.error(f"Download error: {err}")
        return

    file_path = result["file"]
    is_audio = result.get("is_audio", False)

    try:
        await message.answer(t(lang, "success"))
        if is_audio:
            with open(file_path, "rb") as f:
                await message.answer_audio(f)
        else:
            with open(file_path, "rb") as f:
                await message.answer_video(f)

        log_download(user_id, platform, url, quality or "best")

    except Exception as e:
        logger.error(f"Send error: {e}")
        await message.answer(t(lang, "error"))
    finally:
        cleanup_file(file_path)


# ─── Handlerlar ────────────────────────────────────────────────

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    user = message.from_user
    add_user(user.id, user.username or "", user.full_name or "")
    lang = get_user_lang(user.id)
    await state.clear()
    await message.answer(t(lang, "start"))


@dp.message(Command("lang"))
async def cmd_lang(message: types.Message):
    lang = get_user_lang(message.from_user.id)
    await message.answer(t(lang, "choose_lang"), reply_markup=lang_keyboard())


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    lang = get_user_lang(message.from_user.id)
    await message.answer(t(lang, "help"))


@dp.message(Command("stats"))
async def cmd_stats(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        lang = get_user_lang(message.from_user.id)
        await message.answer(t(lang, "not_admin"))
        return
    stats = get_stats()
    lang = get_user_lang(message.from_user.id)
    await message.answer(t(lang, "stats", **stats))


# Til tanlash callback
@dp.callback_query(F.data.startswith("lang_"))
async def cb_lang(callback: types.CallbackQuery):
    lang = callback.data.split("_")[1]
    set_user_lang(callback.from_user.id, lang)
    await callback.message.edit_text(t(lang, "lang_set"))
    await callback.answer()


# Obuna tekshirish callback
@dp.callback_query(F.data == "check_sub")
async def cb_check_sub(callback: types.CallbackQuery):
    lang = get_user_lang(callback.from_user.id)
    ok = await check_subscription(callback.from_user.id)
    if ok:
        await callback.message.edit_text(t(lang, "subscribed_ok"))
    else:
        await callback.answer(t(lang, "not_subscribed"), show_alert=True)


# YouTube sifat tanlash callback
@dp.callback_query(F.data.startswith("q_"))
async def cb_quality(callback: types.CallbackQuery, state: FSMContext):
    lang = get_user_lang(callback.from_user.id)
    quality_map = {
        "q_360": "360p",
        "q_720": "720p",
        "q_1080": "1080p",
        "q_mp3": "mp3",
        "q_cancel": None,
    }
    quality_key = callback.data
    if quality_key == "q_cancel":
        await state.clear()
        await callback.message.edit_text(t(lang, "send_link"))
        await callback.answer()
        return

    data = await state.get_data()
    url = data.get("url")
    if not url:
        await callback.answer("❌ URL topilmadi", show_alert=True)
        await state.clear()
        return

    quality = quality_map.get(quality_key, "720p")
    await callback.message.delete()
    await state.clear()
    await do_download(callback.message, url, quality, lang)
    await callback.answer()


# URL qabul qilish
@dp.message(F.text)
async def handle_url(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    add_user(user_id, message.from_user.username or "", message.from_user.full_name or "")
    lang = get_user_lang(user_id)
    url = message.text.strip()

    # URL emasligini tekshirish
    if not url.startswith("http"):
        return

    # Obuna tekshirish
    if REQUIRED_CHANNEL:
        ok = await check_subscription(user_id)
        if not ok:
            await message.answer(
                t(lang, "subscribe_required", channel=REQUIRED_CHANNEL),
                reply_markup=subscribe_keyboard(lang)
            )
            return

    platform = detect_platform(url)

    if platform == "unknown":
        await message.answer(t(lang, "unsupported"))
        return

    # YouTube uchun sifat tanlash
    if platform == "youtube":
        await state.set_state(DownloadStates.waiting_quality)
        await state.update_data(url=url)
        await message.answer(
            t(lang, "choose_quality"),
            reply_markup=quality_keyboard(lang)
        )
        return

    # Boshqa platformalar
    await do_download(message, url, lang=lang)


# ─── Main ──────────────────────────────────────────────────────
async def main():
    init_db()
    logger.info("🦖 Grabzilla Bot ishga tushdi!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
