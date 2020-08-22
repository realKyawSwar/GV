from showa.modules import config
from showa.lib.database import Postgres
from showa.lib import logs


def uploadDB(df, comPort):
    myPg = None
    try:
        myPg = Postgres(config.url, config.database, config.user,
                        config.password)
        myPg.connect()
        print("Connection succeeded..")
        listy = df.to_csv(None, header=False, index=False).split('\n')
        vals = [','.join(ele.split()) for ele in listy]
        for i in vals:
            y = i.split(",")
            y[0: 2] = [' '.join(y[0: 2])]
            x = tuple(y)
            if x == ('',):
                pass
            else:
                strSQL = "INSERT INTO tdu.{} values {}".format(
                         config.schema, x)
                myPg.execute(strSQL)
        myPg.commit()
    except Exception as err:
        logs.logError(
            "Upload Error Occured: {}".format(str(err)), includeErrorLine=True)
    finally:
        if myPg is not None:
            myPg.close()
