"""個別銘柄の調査に使うツール関数群。

ADK の FunctionTool から呼び出される想定のため、各関数は
・引数はプリミティブ型のみ
・戻り値は dict / list[dict] のみ
・例外を投げず、失敗時は {"error": "..."} を返す
という規約に統一している。
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

import numpy as np
import pandas as pd
import requests
import yfinance as yf

_JST = timezone(timedelta(hours=9))
_REQUEST_TIMEOUT = 10
_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def _to_ticker_symbol(ticker: str) -> str:
    """4桁の証券コードなら東証ティッカー（例: 7203.T）に変換する。"""
    ticker = ticker.strip().upper()
    if ticker.isdigit():
        return f"{ticker}.T"
    return ticker


def _safe_float(value) -> float | None:
    if value is None:
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    if np.isnan(result):
        return None
    return result


def get_stock_price(ticker: str) -> dict:
    """yfinanceで現在の株価情報を取得する。

    Args:
        ticker: 証券コード（例: "7203" または "7203.T"）。

    Returns:
        現在値・前日終値・騰落率・出来高・時価総額などを含む dict。
    """
    symbol = _to_ticker_symbol(ticker)
    try:
        stock = yf.Ticker(symbol)
        history = stock.history(period="5d", interval="1d")
        if history.empty:
            return {"error": f"{symbol} の株価データが取得できませんでした。"}

        info = stock.info or {}
        latest = history.iloc[-1]
        previous_close = (
            _safe_float(history.iloc[-2]["Close"])
            if len(history) >= 2
            else _safe_float(info.get("previousClose"))
        )
        current_price = _safe_float(latest["Close"])
        change = None
        change_percent = None
        if current_price is not None and previous_close:
            change = current_price - previous_close
            change_percent = change / previous_close * 100

        return {
            "ticker": symbol,
            "company_name": info.get("shortName") or info.get("longName"),
            "currency": info.get("currency", "JPY"),
            "current_price": current_price,
            "previous_close": previous_close,
            "change": change,
            "change_percent": change_percent,
            "day_high": _safe_float(latest.get("High")),
            "day_low": _safe_float(latest.get("Low")),
            "volume": _safe_float(latest.get("Volume")),
            "market_cap": _safe_float(info.get("marketCap")),
            "fifty_two_week_high": _safe_float(info.get("fiftyTwoWeekHigh")),
            "fifty_two_week_low": _safe_float(info.get("fiftyTwoWeekLow")),
            "as_of": latest.name.strftime("%Y-%m-%d"),
        }
    except Exception as exc:  # noqa: BLE001
        return {"error": f"株価取得に失敗しました: {exc}"}


def _calc_rsi(close: pd.Series, period: int = 14) -> float | None:
    if len(close) < period + 1:
        return None
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return _safe_float(rsi.iloc[-1])


def _calc_macd(
    close: pd.Series,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> dict:
    if len(close) < slow + signal:
        return {"macd": None, "signal": None, "histogram": None}
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return {
        "macd": _safe_float(macd_line.iloc[-1]),
        "signal": _safe_float(signal_line.iloc[-1]),
        "histogram": _safe_float(histogram.iloc[-1]),
    }


def _calc_bollinger_bands(close: pd.Series, period: int = 20, num_std: float = 2.0) -> dict:
    if len(close) < period:
        return {"upper": None, "middle": None, "lower": None, "percent_b": None}
    window = close.rolling(window=period)
    middle = window.mean()
    std = window.std()
    upper = middle + num_std * std
    lower = middle - num_std * std

    upper_last = _safe_float(upper.iloc[-1])
    lower_last = _safe_float(lower.iloc[-1])
    close_last = _safe_float(close.iloc[-1])
    percent_b = None
    if upper_last is not None and lower_last is not None and upper_last != lower_last:
        percent_b = (close_last - lower_last) / (upper_last - lower_last)

    return {
        "upper": upper_last,
        "middle": _safe_float(middle.iloc[-1]),
        "lower": lower_last,
        "percent_b": percent_b,
    }


def _calc_moving_averages(close: pd.Series) -> dict:
    result = {}
    for period in (5, 25, 75):
        if len(close) >= period:
            result[f"ma{period}"] = _safe_float(close.rolling(window=period).mean().iloc[-1])
        else:
            result[f"ma{period}"] = None
    return result


def get_technical_indicators(ticker: str) -> dict:
    """RSI, MACD, ボリンジャーバンド, 移動平均線(5/25/75日)を計算して返す。

    Args:
        ticker: 証券コード（例: "7203" または "7203.T"）。

    Returns:
        各テクニカル指標と、直近終値との比較から導いたトレンド判定を含む dict。
    """
    symbol = _to_ticker_symbol(ticker)
    try:
        history = yf.Ticker(symbol).history(period="1y", interval="1d")
        if history.empty:
            return {"error": f"{symbol} の株価履歴が取得できませんでした。"}

        close = history["Close"].dropna()
        current_price = _safe_float(close.iloc[-1])
        moving_averages = _calc_moving_averages(close)

        trend = "不明"
        ma5, ma25, ma75 = (
            moving_averages["ma5"],
            moving_averages["ma25"],
            moving_averages["ma75"],
        )
        if ma5 is not None and ma25 is not None and ma75 is not None:
            if ma5 > ma25 > ma75:
                trend = "上昇トレンド（短期>中期>長期）"
            elif ma5 < ma25 < ma75:
                trend = "下降トレンド（短期<中期<長期）"
            else:
                trend = "レンジ・トレンド転換の可能性"

        return {
            "ticker": symbol,
            "current_price": current_price,
            "rsi_14": _calc_rsi(close),
            "macd": _calc_macd(close),
            "bollinger_bands": _calc_bollinger_bands(close),
            "moving_averages": moving_averages,
            "trend": trend,
            "as_of": close.index[-1].strftime("%Y-%m-%d"),
        }
    except Exception as exc:  # noqa: BLE001
        return {"error": f"テクニカル指標の計算に失敗しました: {exc}"}


def get_fundamental_data(ticker: str) -> dict:
    """PER, PBR, ROE, EPS成長率, 配当利回り, 売上成長率, 自己資本比率, キャッシュフローを取得する。

    Args:
        ticker: 証券コード（例: "7203" または "7203.T"）。

    Returns:
        バリュエーション・収益性・成長性・財務健全性・キャッシュフローに関する指標を含む dict。
    """
    symbol = _to_ticker_symbol(ticker)
    try:
        stock = yf.Ticker(symbol)
        info = stock.info or {}

        eps_growth = _safe_float(info.get("earningsQuarterlyGrowth"))
        revenue_growth = _safe_float(info.get("revenueGrowth"))
        # yfinance の dividendYield は既にパーセント表記（例: 3.36 = 3.36%）で返る。
        dividend_yield_percent = _safe_float(info.get("dividendYield"))

        operating_cashflow = _safe_float(info.get("operatingCashflow"))
        free_cashflow = _safe_float(info.get("freeCashflow"))

        equity_ratio = None
        total_assets = _safe_float(info.get("totalAssets"))
        stockholders_equity = None
        try:
            balance_sheet = stock.balance_sheet
            if balance_sheet is not None and not balance_sheet.empty:
                latest_col = balance_sheet.columns[0]
                if "Stockholders Equity" in balance_sheet.index:
                    stockholders_equity = _safe_float(
                        balance_sheet.loc["Stockholders Equity", latest_col]
                    )
                if total_assets is None and "Total Assets" in balance_sheet.index:
                    total_assets = _safe_float(balance_sheet.loc["Total Assets", latest_col])
        except Exception:  # noqa: BLE001
            pass

        if stockholders_equity is not None and total_assets:
            equity_ratio = stockholders_equity / total_assets * 100

        return {
            "ticker": symbol,
            "per": _safe_float(info.get("trailingPE")),
            "forward_per": _safe_float(info.get("forwardPE")),
            "pbr": _safe_float(info.get("priceToBook")),
            "roe": (
                _safe_float(info.get("returnOnEquity")) * 100
                if info.get("returnOnEquity") is not None
                else None
            ),
            "roa": (
                _safe_float(info.get("returnOnAssets")) * 100
                if info.get("returnOnAssets") is not None
                else None
            ),
            "eps": _safe_float(info.get("trailingEps")),
            "eps_growth_percent": eps_growth * 100 if eps_growth is not None else None,
            "revenue_growth_percent": (
                revenue_growth * 100 if revenue_growth is not None else None
            ),
            "dividend_yield_percent": dividend_yield_percent,
            "payout_ratio_percent": (
                _safe_float(info.get("payoutRatio")) * 100
                if info.get("payoutRatio") is not None
                else None
            ),
            "equity_ratio_percent": equity_ratio,
            "operating_cashflow": operating_cashflow,
            "free_cashflow": free_cashflow,
            "profit_margin_percent": (
                _safe_float(info.get("profitMargins")) * 100
                if info.get("profitMargins") is not None
                else None
            ),
            "industry": info.get("industry"),
            "sector": info.get("sector"),
        }
    except Exception as exc:  # noqa: BLE001
        return {"error": f"ファンダメンタルデータの取得に失敗しました: {exc}"}


def get_macro_indicators() -> dict:
    """USD/JPY, VIX, CME日経先物, 米10年債利回りを取得する。

    Returns:
        各マクロ指標の現在値と前日比を含む dict。
    """
    symbols = {
        "usd_jpy": "JPY=X",
        "vix": "^VIX",
        "nikkei_futures": "NIY=F",
        "us_10y_treasury_yield": "^TNX",
    }
    result: dict = {}
    for key, symbol in symbols.items():
        try:
            history = yf.Ticker(symbol).history(period="5d", interval="1d")
            if history.empty:
                result[key] = {"error": f"{symbol} のデータが取得できませんでした。"}
                continue

            latest = _safe_float(history["Close"].iloc[-1])
            previous = (
                _safe_float(history["Close"].iloc[-2]) if len(history) >= 2 else None
            )
            change_percent = None
            if latest is not None and previous:
                change_percent = (latest - previous) / previous * 100

            result[key] = {
                "value": latest,
                "change_percent": change_percent,
                "as_of": history.index[-1].strftime("%Y-%m-%d"),
            }
        except Exception as exc:  # noqa: BLE001
            result[key] = {"error": f"取得に失敗しました: {exc}"}

    return result


def search_news(company_name: str) -> list[dict]:
    """直近1週間のニュースをGoogleニュースのRSSフィードから取得する。

    Args:
        company_name: 検索対象の企業名または証券コード。

    Returns:
        タイトル・リンク・公開日を含むニュース記事の dict のリスト
        （直近1週間分、新しい順）。
    """
    try:
        query = quote(company_name)
        # Google ニュースの検索結果RSS（日本語・日本地域）を利用する
        search_url = f"https://news.google.com/rss/search?q={query}&hl=ja&gl=JP&ceid=JP:ja"
        response = requests.get(
            search_url,
            headers={"User-Agent": _USER_AGENT},
            timeout=_REQUEST_TIMEOUT,
        )
        response.raise_for_status()

        root = ET.fromstring(response.content)
        one_week_ago = datetime.now(_JST) - timedelta(days=7)

        articles = []
        for item in root.findall(".//item"):
            title = item.findtext("title") or ""
            link = item.findtext("link") or ""
            pub_date_raw = item.findtext("pubDate")

            published_at = None
            if pub_date_raw:
                try:
                    published_at = pd.to_datetime(pub_date_raw, utc=True).tz_convert(_JST)
                except Exception:  # noqa: BLE001
                    published_at = None

            if published_at is not None and published_at < one_week_ago:
                continue

            articles.append(
                {
                    "title": title,
                    "link": link,
                    "published_at": (
                        published_at.strftime("%Y-%m-%d %H:%M")
                        if published_at is not None
                        else None
                    ),
                }
            )

        articles.sort(key=lambda a: a["published_at"] or "", reverse=True)
        return articles[:20]
    except Exception as exc:  # noqa: BLE001
        return [{"error": f"ニュース取得に失敗しました: {exc}"}]
