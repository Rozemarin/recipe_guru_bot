import logging
from random import randint

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)
    
recipe_collection = {}

ADD_RECIPE_NAME, ADD_RECIPE_DESCRIPTION = range(2)
EDIT_RECIPE_NAME, EDIT_RECIPE_DESCRIPTION = range(2)
DELETE_RECIPE_NAME = range(1)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Я бот для рецепт-менеджмента, подробнее о командах можно узнать в моем меню!")

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("Started adding recipe from: %s", user.first_name)
    await update.message.reply_text(
        "Сейчас мы будем сохранять ваш рецепт!"
        " Отправьте /cancel, если решили, что мир ещё не готов к вашему шедевру.\n\n"
        "Начнем с малого. Как называется ваш рецепт?",
    )
    return ADD_RECIPE_NAME


async def recipe_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("gettimg recipe name from: %s", user.first_name)
    if user.id in recipe_collection and update.message.text in recipe_collection[user.id]:
        await update.message.reply_text(
        "У вас уже есть такой рецепт. Вы можете его исправить или удалить. Для этого отправьте /edit или /delete <имя рецепта>"
        )
        return ConversationHandler.END

    context.user_data["name"] = update.message.text
    logger.info("Name of recepi of %s: %s", user.first_name, update.message.text)
    await update.message.reply_text(
        "Отлично! Теперь расскажите, как приготовить ваше замечательное блюдо"
    )

    return ADD_RECIPE_DESCRIPTION


async def recipe_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("getting recipe description from: %s", user.first_name)
    context.user_data["description"] = update.message.text
    logger.info("Bio of %s: %s", user.first_name, update.message.text)

    if user.id not in recipe_collection:
        recipe_collection[user.id] = {}

    recipe_collection[user.id][context.user_data["name"]] = context.user_data["description"];
    await update.message.reply_text("Спасибо! Я сохранил ваш рецепт.")
    print(recipe_collection)
    context.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "До связи!", reply_markup=ReplyKeyboardRemove()
    )
    context.user_data.clear()
    return ConversationHandler.END


async def get_random(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    logger.info("getting random from: %s", user.first_name)
    if user.id not in recipe_collection or not recipe_collection[user.id]:
        await update.message.reply_text("У вас ещё нет рецептов :( Хотите добавить? Нажмите /add")
        return

    x = randint(0, len(recipe_collection[user.id].keys()) - 1)
    name = list(recipe_collection[user.id].keys())[x]
    desc = recipe_collection[user.id][name]
    ans = f"Название: {name}\n\nОписание: {desc}"
    await update.message.reply_text(ans)


async def edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("start editing from: %s", user.first_name)
    await update.message.reply_text(
        "Что-то забыли? Введите имя рецепта, который хотите исправить"
        " Отправьте /cancel, если решили, что все и так прекрасно",
    )

    return EDIT_RECIPE_NAME


async def edit_recipe_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("start name edit from %s", user.first_name)
    if user.id not in recipe_collection or update.message.text not in recipe_collection[user.id]:
        await update.message.reply_text("Вы не добавляли такго рецепта :( Может быть вы хотите это исправить? Нажмите /add",)
        return ConversationHandler.END
    
    logger.info("continue editing %s", user.first_name)
    context.user_data["name"] = update.message.text
    old_desc = recipe_collection[user.id][context.user_data["name"]]
    logger.info("Finish of editing recepi of %s: %s", user.first_name, update.message.text)
    await update.message.reply_text(
        f"Вот каким было описание раньше: {old_desc}\n\n"
        "Отправьте мне новое, а я всё запишу куда надо"
    )

    return EDIT_RECIPE_DESCRIPTION


async def edit_recipe_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("started changing desc %s", user.first_name)
    context.user_data["description"] = update.message.text
    logger.info("changed desc %s", user.first_name)

    recipe_collection[user.id][context.user_data["name"]] = context.user_data["description"];
    await update.message.reply_text("Спасибо! Рецепт изменен")
    print(recipe_collection)
    context.user_data.clear()
    return ConversationHandler.END


async def view_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    logger.info("viewing all %s", user.first_name)
    if user.id not in recipe_collection or not recipe_collection[user.id]:
        await update.message.reply_text("Вы ещё не добавляли рецептов. Но это можно исправить! Нажмите /add")
        return
    
    ans = ""
    for name, desc in recipe_collection[user.id].items():
        ans += f"Название: {name}\nОписание: {desc}\n\n"
    await update.message.reply_text(ans.strip())


async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("started deleting %s", user.first_name)
    await update.message.reply_text(
        "Введите название рецепта, который хотите удалить"
        " Отправьте /cancel, если решили, что передумали",
    )

    return DELETE_RECIPE_NAME


async def delete_recipe_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    name = update.message.text

    logger.info("continue deleting %s", user.first_name)

    if user.id not in recipe_collection or name not in recipe_collection[user.id]:
        await update.message.reply_text("Вы не добавляли такго рецепта :(",)
        return ConversationHandler.END
    
    logger.info("really deleting %s", user.first_name)
    del recipe_collection[user.id][name]
    logger.info("Name of recepi of %s: %s", user.first_name, update.message.text)
    await update.message.reply_text(f'Рецепт "{name}" удален!')

    return ConversationHandler.END


def main() -> None:     
    application = Application.builder().token("TOKEN").build()

    conv_handler_add = ConversationHandler(
        entry_points=[CommandHandler("add", add)],
        states={
            ADD_RECIPE_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, recipe_name)],
            ADD_RECIPE_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, recipe_description)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    conv_handler_edit = ConversationHandler(
        entry_points=[CommandHandler("edit", edit)],
        states={
            EDIT_RECIPE_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_recipe_name)],
            EDIT_RECIPE_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_recipe_description)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    conv_handler_delete = ConversationHandler(
        entry_points=[CommandHandler("delete", delete)],
        states={
            DELETE_RECIPE_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, delete_recipe_name)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    application.add_handler(conv_handler_add)
    application.add_handler(conv_handler_edit)  
    application.add_handler(conv_handler_delete)
    application.add_handler(CommandHandler("get_random", get_random))
    application.add_handler(CommandHandler("view_all", view_all))

    application.run_polling()


if __name__ == "__main__":
    main()