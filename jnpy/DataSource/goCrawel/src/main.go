package main

import (
	"context"
	"encoding/csv"
	"flag"
	"fmt"
	goex "github.com/nntaoli-project/GoEx"
	"github.com/nntaoli-project/GoEx/binance"
	"log"
	"net/http"
	"net/url"
	"os"
	"os/signal"
	"time"
)

var (
	beginTime    = time.Date(2017, 12, 18, 0, 0, 0, 0, time.Local) //开始时间2019年8月18日,需自行修改
	klinePeriod  = goex.KLINE_PERIOD_1MIN                         //see: github.com/nntaoli-project/GoEx/Const.go
	currencyPair = goex.LTC_USDT
	fileDir string

	csvWriterM map[string]*csv.Writer
	fileM      map[string]*os.File
)

func init() {
	csvWriterM = make(map[string]*csv.Writer, 10)
	fileM = make(map[string]*os.File, 10)
}

func csvWriter(timestamp int64) *csv.Writer {
	t := time.Unix(timestamp, 0).Format("2006-01-02")
	p := "1min"
	switch klinePeriod {
	case goex.KLINE_PERIOD_1MIN:
		p = "1min"
	case goex.KLINE_PERIOD_5MIN:
		p = "5min"
	case goex.KLINE_PERIOD_30MIN:
		p = "30min"
	case goex.KLINE_PERIOD_1H:
		p = "1h"
	case goex.KLINE_PERIOD_4H:
		p = "4h"
	case goex.KLINE_PERIOD_1DAY:
		p = "1day"
	}

	err := os.MkdirAll(fileDir,os.ModePerm)
	if err!=nil{
		fmt.Println(err)
	}

	fileName := fmt.Sprintf("%s/binance_kline_%s_%s_%s.csv", fileDir, currencyPair.ToLower().ToSymbol(""), p, t)

	w := csvWriterM[fileName]
	if w != nil {
		return w
	}

	f, err := os.OpenFile(fileName, os.O_WRONLY|os.O_CREATE|os.O_TRUNC, 0766)
	if err != nil {
		panic(err)
	}

	w = csv.NewWriter(f)

	csvWriterM[fileName] = w
	fileM[fileName] = f

	return w
}

func main() {

	// cmd>./main date 2019-12-20 time 00:00:00 period 1MIN currencyPair BTC_CNY dir

	beginDate_str := flag.String(
		"date", "2019-12-18", "enter date format: 2017-12-18")
	beginTime_str := flag.String(
		"time", "00:00:00", "enter time format: 00:00:00")
	beginDateTime_str := fmt.Sprintf("%s %s", *beginDate_str, *beginTime_str)
	log.Println(beginDateTime_str)
	local, _ := time.LoadLocation("Local")
	beginTime, err := time.ParseInLocation("2006-01-02 15:04:05", beginDateTime_str, local)
	if err != nil{
		log.Println(err)
		return
	}

	periodArgStr := flag.String(
		"period", "1MIN", "enter period format: 1MIN/1H/1DAY/1WEEK/1MONTH/1YEAR")
	currencyPairArgStr := flag.String(
		"currencyPair", "BTC_USDT", "enter currencyPair format: LTC_USDT")
	//beginTime    = time.Date(2017, 12, 18, 0, 0, 0, 0, time.Local) //开始时间2019年8月18日,需自行修改
	//klinePeriod  = goex.KLINE_PERIOD_1MIN                         //see: github.com/nntaoli-project/GoEx/Const.go
	klinePeriod  = KlinePeriodM[*periodArgStr]                      //see: github.com/nntaoli-project/GoEx/Const.go
	currencyPair = CurrencyPairM[*currencyPairArgStr]

	dirStr := flag.String("dir","./data", "enter fileDir format: ./xxx")
	fileDir = *dirStr

	log.Println("begin download kline")

	ctx, cancel := context.WithCancel(context.Background())

	go func() {
		c := make(chan os.Signal, 1)
		signal.Notify(c, os.Interrupt, os.Kill)
		<-c
		cancel()
	}()

	defer func() {
		for _, w := range csvWriterM {
			w.Flush()
		}

		for _, f := range fileM {
			f.Close()
		}

		log.Println("end")
	}()

	ba := binance.NewWithConfig(&goex.APIConfig{
		//HttpClient: http.DefaultClient,
		HttpClient: &http.Client{
			Transport: &http.Transport{
				Proxy: func(request *http.Request) (*url.URL, error) {
					return url.Parse("socks5://127.0.0.1:1080") //ss proxy
				},
			},
			Timeout: 10 * time.Second,
		},
	})

	since := int(beginTime.Unix()) * 1000
	interval := time.NewTimer(200 * time.Millisecond)

	for {
		select {
		case <-ctx.Done():
			return
		case <-interval.C:
			klines, err := ba.GetKlineRecords(currencyPair, klinePeriod, 1000, since)
			if err != nil {
				log.Println(err)
				interval.Reset(200 * time.Millisecond)
				continue
			}

			for _, k := range klines {
				csvWriter(k.Timestamp).Write([]string{fmt.Sprint(k.Timestamp), goex.FloatToString(k.High, 8),
					goex.FloatToString(k.Low, 8), goex.FloatToString(k.Open, 8), goex.FloatToString(k.Close, 8), goex.FloatToString(k.Vol, 8)})
			}

			since = int(klines[len(klines)-1].Timestamp)*1000 + 1
			if len(klines) < 1000 {
				cancel()
			}

			interval.Reset(200 * time.Millisecond)
		}
	}
}
