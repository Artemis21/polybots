# Tiny Tourney Two Bot

## Config

Configuration goes in `config.json`. It is a JSON file containing a single JSON object with the following fields:

| Field                   | Default        | Purpose                               |
|:-----------------------:|:--------------:|:--------------------------------------|
| `bot_prefix`            | `t!`           | The command prefix for the bot.       |
| `bot_token`             | Required       | The auth token for the Discord bot.   |
| `bot_admin_role_id`     | Required       | The ID of the tourney manager role.   |
| `bot_log_channel_id`    | `null`         | The ID of the channel to send logs to.|
| `bot_guild_id`          | Required       | The ID of the Discord server to use.  |
| `bot_log_level`         | `INFO`         | The logging level for Discord.py.     |
| `elo_base_url`          | Below <sup>*1</sup> | The address of the ELO bot API.  |
| `elo_username`          | Required       | The username for the ELO bot API.     |
| `elo_password`          | Required       | The password for the ELO bot API.     |
| `elo_recheck_time`      | `13h`          | Time to wait before rechecking games. |
| `elo_recheck_frequency` | `30m`          | Frequency to recheck pending games.   |
| `elo_guild_id`          | Required       | The ID of the server teams are for.   |
| `db_name`               | `ttt`          | The name of the PostgreSQL database.  |
| `db_user`               | `ttt`          | The user to use for the database.     |
| `db_host`               | `127.0.0.1`    | The host address of the database.     |
| `db_port`               | `5432`         | The port to access the database on.   |
| `db_password`           | Required       | The password for the database.        |
| `db_log_level`          | `INFO`         | The logging level for Peewee.         |
| `col_accent`            | `#c64191`      | The accent colour for the bot.        |
| `col_error`             | `#e94b3c`      | The error colour for the bot.         |
| `col_help`              | `#50c878`      | The help colour for the bot.          |
| `tt_game_types`         | See Appendix A | A list of game types.                 |
| `tt_log_level`          | `INFO`         | Logging level for log channel.        |

<sup>*1</sup> `https://elo-bot.polytopia.win`

## Appendix A: Default Game Types

In the config file, game types should be specified as a list of objects, each having the keys `map`, `tribe` and `alt_tribe`.

The default list is below:

| Map Type    | Tribe    | Alternative Tribe |
|:-----------:|:--------:|:-----------------:|
| Dryland     | Yadakk   | Oumaji            |
| Lakes       | Luxidoor | Bardur            |
| Continents  | Zebasi   | Imperius          |
| Archipelago | Polaris  | Imperius          |
| Drylands    | Hoodrick | Bardur            |
| Continents  | Cymanti  | Bardur            |
| Water World | Vengir   | Oumaji            |
| Lakes       | Queztali | Xin-xi            |
| Dryland     | Ai-Mo    | Xin-xi            |
| Lakes       | Elyrion  | Imperius          |
| Archipelago | Aquarion | Oumaji            |
| Continents  | Kickoo   | Xin-xi            |
