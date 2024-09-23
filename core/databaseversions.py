from core.databasemodule import databaseHandler as db

class databaseVersions:

    def Sergal_v1(localize:db, version) -> list:
        if version == 0:
            steps = [
                lambda: db.tableExist(self=localize, table="stat", make=True),
                lambda: db.defineColumn(
                    self=localize,
                    name="stat",
                    dataType=db.dataTypes.TINYTEXT,
                    unique=True
                ),
                lambda: db.defineColumn(
                    self=localize,
                    name="textval", 
                    dataType=db.dataTypes.TEXT
                ),
                lambda: db.defineColumn(
                    self=localize,
                    name="val", 
                    dataType=db.dataTypes.INT,
                    fin_ex=True
                ),
                lambda: db.tableExist(self=localize, table="settings", make=True),
                lambda: db.defineColumn(
                    self=localize,
                    name="setting",
                    dataType=db.dataTypes.TINYTEXT,
                    unique=True
                ),
                lambda: db.defineColumn(
                    self=localize,
                    name="setting_val",
                    dataType=db.dataTypes.INT,
                ),
                lambda: db.defineColumn(
                    self=localize,
                    name="setting_text",
                    dataType=db.dataTypes.TEXT,
                    fin_ex=True
                ),
                lambda: db.tableExist(self=localize,table="errors", make=True),
                lambda: db.defineColumn(
                    self=localize,
                    name="ID",
                    dataType=db.dataTypes.INT,
                    auto_inc=True,
                    primaryKey=True
                ),
                lambda: db.defineColumn(
                    self=localize,
                    name="type",
                    dataType=db.dataTypes.TINYTEXT
                ),
                lambda: db.defineColumn(
                    self=localize,
                    name="info",
                    dataType=db.dataTypes.TEXT,
                    fin_ex=True
                ),
                lambda: db.tableExist(
                    self=localize,
                    table="channel_settings",
                    make=True
                ),
                lambda: db.defineColumn(
                    self=localize,
                    name="guild_id",
                    dataType=db.dataTypes.BIGINT,
                    primaryKey=True,
                    notNull=True
                ),
                lambda: db.defineColumn(
                    self=localize,
                    name="channel_id",
                    dataType=db.dataTypes.BIGINT,
                    notNull=True
                ),
                lambda: db.defineColumn(
                    self=localize,
                    name="setting",
                    dataType=db.dataTypes.TINYTEXT,
                    notNull=True,
                    fin_ex=True
                ),
                lambda: db.insertRawCommand(
                    self=localize,
                    command="ALTER TABLE `errors` ADD `was_read` TINYINT NOT NULL DEFAULT '0' AFTER `info`;\n"
                ),
                lambda: db.wrapex(self=localize, insert=True),
                lambda: db.insert(
                    self=localize,
                    table="settings",
                    columns=["setting", "setting_val"],
                    data=["db_ver", 1]
                )
            ]
            return steps
        else:
            return []