package main

import goex "github.com/nntaoli-project/GoEx"

var(
	KlinePeriodM = map[string]int{
		"1MIN": goex.KLINE_PERIOD_1MIN,
		"3MIN": goex.KLINE_PERIOD_3MIN,
		"5MIN": goex.KLINE_PERIOD_5MIN,
		"15MIN": goex.KLINE_PERIOD_15MIN,
		"30MIN": goex.KLINE_PERIOD_30MIN,
		"60MIN": goex.KLINE_PERIOD_60MIN,
		"1H": goex.KLINE_PERIOD_1H,
		"2H": goex.KLINE_PERIOD_2H,
		"4H": goex.KLINE_PERIOD_4H,
		"6H": goex.KLINE_PERIOD_6H,
		"8H": goex.KLINE_PERIOD_8H,
		"12H": goex.KLINE_PERIOD_12H,
		"1DAY": goex.KLINE_PERIOD_1DAY,
		"3DAY": goex.KLINE_PERIOD_3DAY,
		"1WEEK": goex.KLINE_PERIOD_1WEEK,
		"1MONTH": goex.KLINE_PERIOD_1MONTH,
		"1YEAR": goex.KLINE_PERIOD_1YEAR,
	}
	CurrencyPairM = map[string]goex.CurrencyPair{
		//currency pair
		"BTC_CNY"  :goex.BTC_CNY,
		"LTC_CNY"  :goex.LTC_CNY,
		"BCC_CNY"  :goex.BCC_CNY,
		"ETH_CNY"  :goex.ETH_CNY,
		"ETC_CNY"  :goex.ETC_CNY,
		"EOS_CNY"  :goex.EOS_CNY,
		"BTS_CNY"  :goex.BTS_CNY,
		"QTUM_CNY" :goex.QTUM_CNY,
		"SC_CNY"  :goex.SC_CNY,
		"ANS_CNY"  :goex.ANS_CNY,
		"ZEC_CNY"  :goex.ZEC_CNY,

		"BTC_KRW" :goex.BTC_KRW,
		"ETH_KRW" :goex.ETH_KRW,
		"ETC_KRW" :goex.ETC_KRW,
		"LTC_KRW" :goex.LTC_KRW,
		"BCH_KRW" :goex.BCH_KRW,

		"BTC_USD" :goex.BTC_USD,
		"LTC_USD" :goex.LTC_USD,
		"ETH_USD" :goex.ETH_USD,
		"ETC_USD" :goex.ETC_USD,
		"BCH_USD" :goex.BCH_USD,
		"BCC_USD" :goex.BCC_USD,
		"XRP_USD" :goex.XRP_USD,
		"BCD_USD" :goex.BCD_USD,
		"EOS_USD" :goex.EOS_USD,
		"BTG_USD" :goex.BTG_USD,
		"BSV_USD" :goex.BSV_USD,

		"BTC_USDT":goex.BTC_USDT,
		"LTC_USDT":goex.LTC_USDT,
		"BCH_USDT":goex.BCH_USDT,
		"BCC_USDT":goex.BCC_USDT,
		"ETC_USDT":goex.ETC_USDT,
		"ETH_USDT":goex.ETH_USDT,
		"BCD_USDT":goex.BCD_USDT,
		"NEO_USDT":goex.NEO_USDT,
		"EOS_USDT":goex.EOS_USDT,
		"XRP_USDT":goex.XRP_USDT,
		"HSR_USDT":goex.HSR_USDT,
		"BSV_USDT":goex.BSV_USDT,
		"OKB_USDT":goex.OKB_USDT,
		"HT_USDT" :goex.HT_USDT,
		"BNB_USDT":goex.BNB_USDT,
		"PAX_USDT":goex.PAX_USDT,
		"TRX_USDT":goex.TRX_USDT,

		"XRP_EUR" :goex.XRP_EUR,

		"BTC_JPY" :goex.BTC_JPY,
		"LTC_JPY" :goex.LTC_JPY,
		"ETH_JPY" :goex.ETH_JPY,
		"ETC_JPY" :goex.ETC_JPY,
		"BCH_JPY" :goex.BCH_JPY,

		"LTC_BTC" :goex.LTC_BTC,
		"ETH_BTC" :goex.ETH_BTC,
		"ETC_BTC" :goex.ETC_BTC,
		"BCC_BTC" :goex.BCC_BTC,
		"BCH_BTC" :goex.BCH_BTC,
		"DCR_BTC" :goex.DCR_BTC,
		"XRP_BTC" :goex.XRP_BTC,
		"BTG_BTC" :goex.BTG_BTC,
		"BCD_BTC" :goex.BCD_BTC,
		"NEO_BTC" :goex.NEO_BTC,
		"EOS_BTC" :goex.EOS_BTC,
		"HSR_BTC" :goex.HSR_BTC,
		"BSV_BTC" :goex.BSV_BTC,
		"OKB_BTC" :goex.OKB_BTC,
		"HT_BTC" :goex.HT_BTC,
		"BNB_BTC" :goex.BNB_BTC,
		"TRX_BTC" :goex.TRX_BTC,

		"ETC_ETH" :goex.ETC_ETH,
		"EOS_ETH" :goex.EOS_ETH,
		"ZEC_ETH" :goex.ZEC_ETH,
		"NEO_ETH" :goex.NEO_ETH,
		"HSR_ETH" :goex.HSR_ETH,
		"LTC_ETH" :goex.LTC_ETH,

		"UNKNOWN_PAIR" :goex.UNKNOWN_PAIR,
	}
)