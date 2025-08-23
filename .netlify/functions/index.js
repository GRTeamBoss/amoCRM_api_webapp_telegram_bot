import { Telegraf } from "telegraf"

import { Config } from "./config/config.js";

const config = new Config();
const bot = new Telegraf(config.TELEGRAM_TOKEN);

exports.handler = async (event, context) => {
  await bot.handleUpdate(JSON.parse(event.body));
  return {statusCode: 200, body: "OK"};
};

process.once("SIGINT", () => {
  bot.stop("SIGINT");
});

process.once("SIGTERM", () => {
  bot.stop("SIGTERM");
});
