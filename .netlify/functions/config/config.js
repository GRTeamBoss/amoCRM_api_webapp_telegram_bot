import { configDotenv } from "dotenv";

export class Config {
  constructor() {
    configDotenv();
    this.TELEGRAM_TOKEN = process.env.TELEGRAM_TOKEN
    this.ADMINS = process.env.ADMINS.split(",").map(Number);
  }
}
