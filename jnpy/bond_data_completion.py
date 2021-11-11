import datetime
import tqdm

from vnpy.trader.engine import MainEngine, EventEngine
from jnpy.gateway.acestock.acestock.gateway import AcestockGateway
from vnpy.trader.constant import Interval, Product
from vnpy.trader.database import DB_TZ, get_database
from vnpy.trader.object import HistoryRequest

completion_product = Product.BOND

want_interval = Interval.MINUTE_5
want_start_datetime = datetime.datetime(year=2021, month=9, day=1, tzinfo=DB_TZ)
now = datetime.datetime.now(tz=DB_TZ)
if now.time() < datetime.time(hour=9, minute=30, tzinfo=DB_TZ):
    now -= datetime.timedelta(days=1)

if __name__ == '__main__':
    main_engine = MainEngine(EventEngine())
    acestock_gateway = main_engine.add_gateway(AcestockGateway)

    db = get_database()
    overview_dict = {
        f"{overview.symbol}.{overview.exchange.value}_{overview.interval}": overview
        for overview in db.get_bar_overview()
    }

    acestock_gateway.connect_md_api()
    bond_contracts_dict = acestock_gateway.contracts_dict[completion_product]

    for _, contract_data in tqdm.tqdm(bond_contracts_dict.items(), total=len(bond_contracts_dict)):
        overview_dict_key = f"{contract_data.vt_symbol}_{want_interval}"
        if overview_dict_key in overview_dict:
            print(f"数据已存在, 开始检查是否需要补全数据...")
            # 是否要补全更早的数据
            overview_start_datetime = overview_dict[overview_dict_key].start
            if want_start_datetime.date() < overview_start_datetime.date():
                req = HistoryRequest(
                    symbol=contract_data.symbol,
                    exchange=contract_data.exchange,
                    start=want_start_datetime,
                    end=overview_start_datetime,
                    interval=want_interval,
                )
                r = acestock_gateway.query_history(req)
                if r:
                    db.save_bar_data(r)
                    print(f"[前项补全] {len(r)}条数据: {req}")
            else:
                print(f"无需前项补全")

            overview_end_datetime = overview_dict[overview_dict_key].end
            # 根据 date 判断是否要补全更早的数据, 比较适合盘前运行
            if overview_end_datetime.date() < now.date():
                # 追加数据库中 end -> now 的数据
                req = HistoryRequest(
                    symbol=contract_data.symbol,
                    exchange=contract_data.exchange,
                    start=overview_end_datetime,
                    end=now,
                    interval=want_interval,
                )
                r = acestock_gateway.query_history(req)
                if r:
                    db.save_bar_data(r)
                    print(f"[后项补全] {len(r)}条数据: {req}")
            else:
                print(f"无需后项补全")
        else:
            req = HistoryRequest(
                symbol=contract_data.symbol,
                exchange=contract_data.exchange,
                start=want_start_datetime,
                end=now,
                interval=want_interval,
            )
            r = acestock_gateway.query_history(req)
            if r:
                db.save_bar_data(r)
                print(f"[新增] {len(r)}条数据: {req}")

    print("数据补完任务完成")
