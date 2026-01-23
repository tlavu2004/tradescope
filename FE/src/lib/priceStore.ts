// Shared price store - singleton that manages real-time price data for all symbols
// This centralizes WebSocket subscriptions to avoid duplicates
// Uses daily candle API for accurate open price and 1d websocket for 24h volume

import { sharedWs } from './sharedWs';

export interface SymbolPrice {
  symbol: string;
  price: number;
  dailyOpen: number;     // Open price from daily candle (for change calculation)
  high: number;
  low: number;
  close: number;
  change: number;        // price - dailyOpen
  changePercent: number; // (change / dailyOpen) * 100
  volume24h: number;     // 24h volume from 1d candle
  lastUpdate: number;
}

interface DailyCandle {
  symbol: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

type PriceListener = (prices: Map<string, SymbolPrice>) => void;

const API_BASE = `${(import.meta.env.VITE_API_BASE as string) || 'http://localhost'}/api/v1`;

class PriceStore {
  private prices: Map<string, SymbolPrice> = new Map();
  private listeners: Set<PriceListener> = new Set();
  private subscriptions: Map<string, () => void> = new Map();
  private dailyOpenPrices: Map<string, number> = new Map();
  private dailyVolumes: Map<string, number> = new Map();
  private initialized: Set<string> = new Set();

  // Fetch daily candle from API for open price
  private async fetchDailyCandle(symbol: string): Promise<DailyCandle | null> {
    try {
      const token = localStorage.getItem('accessToken');
      const response = await fetch(`${API_BASE}/candles/latest-candle?interval=1d`, {
        headers: token ? { 'Authorization': `Bearer ${token}` } : {},
      });

      if (!response.ok) {
        console.warn(`Failed to fetch daily candle for ${symbol}:`, response.status);
        return null;
      }

      const data = await response.json();
      // API returns array of candles, find the one for this symbol
      const candle = Array.isArray(data)
        ? data.find((c: any) => c.symbol === symbol)
        : data.symbol === symbol ? data : null;

      if (candle) {
        return {
          symbol: candle.symbol,
          open: Number(candle.open),
          high: Number(candle.high),
          low: Number(candle.low),
          close: Number(candle.close),
          volume: Number(candle.volume),
        };
      }
      return null;
    } catch (e) {
      console.error(`Error fetching daily candle for ${symbol}:`, e);
      return null;
    }
  }

  // Subscribe to a symbol's price updates
  async subscribe(symbol: string) {
    // Check if already subscribed (using both 1m and 1d)
    const key1m = `${symbol}:1m`;
    const key1d = `${symbol}:1d`;

    if (this.subscriptions.has(key1m)) {
      return; // Already subscribed
    }

    // Fetch initial daily candle for open price and volume
    if (!this.initialized.has(symbol)) {
      const dailyCandle = await this.fetchDailyCandle(symbol);
      if (dailyCandle) {
        this.dailyOpenPrices.set(symbol, dailyCandle.open);
        this.dailyVolumes.set(symbol, dailyCandle.volume);
        console.log(`[PriceStore] ${symbol} daily open: ${dailyCandle.open}, volume: ${dailyCandle.volume}`);
      }
      this.initialized.add(symbol);
    }

    // Handler for 1m candles (current price updates)
    const handler1m = (candle: any) => {
      const closePrice = Number(candle.close);
      const dailyOpen = this.dailyOpenPrices.get(symbol) || closePrice;
      const volume24h = this.dailyVolumes.get(symbol) || 0;

      const change = closePrice - dailyOpen;
      const changePercent = dailyOpen > 0 ? (change / dailyOpen) * 100 : 0;

      const priceData: SymbolPrice = {
        symbol,
        price: closePrice,
        dailyOpen,
        high: Number(candle.high),
        low: Number(candle.low),
        close: closePrice,
        change,
        changePercent,
        volume24h,
        lastUpdate: Date.now(),
      };

      this.prices.set(symbol, priceData);
      this.notifyListeners();
    };

    // Handler for 1d candles (volume updates)
    const handler1d = (candle: any) => {
      const volume = Number(candle.volume) || 0;
      const openPrice = Number(candle.open);

      // Update daily data
      this.dailyVolumes.set(symbol, volume);
      // Only update open if we don't have it yet (start of new day)
      if (!this.dailyOpenPrices.has(symbol)) {
        this.dailyOpenPrices.set(symbol, openPrice);
      }

      // Update price data with new volume
      const existing = this.prices.get(symbol);
      if (existing) {
        existing.volume24h = volume;
        this.prices.set(symbol, existing);
        this.notifyListeners();
      }
    };

    // Subscribe to both 1m and 1d
    const unsub1m = sharedWs.subscribe(symbol, handler1m, '1m');
    const unsub1d = sharedWs.subscribe(symbol, handler1d, '1d');

    this.subscriptions.set(key1m, unsub1m);
    this.subscriptions.set(key1d, unsub1d);
  }

  // Unsubscribe from a symbol
  unsubscribe(symbol: string) {
    const key1m = `${symbol}:1m`;
    const key1d = `${symbol}:1d`;

    const unsub1m = this.subscriptions.get(key1m);
    const unsub1d = this.subscriptions.get(key1d);

    if (unsub1m) {
      unsub1m();
      this.subscriptions.delete(key1m);
    }
    if (unsub1d) {
      unsub1d();
      this.subscriptions.delete(key1d);
    }
  }

  // Subscribe multiple symbols at once
  async subscribeAll(symbols: string[]) {
    await Promise.all(symbols.map((sym) => this.subscribe(sym)));
  }

  // Add a listener for price changes
  addListener(listener: PriceListener): () => void {
    this.listeners.add(listener);
    // Immediately notify with current data
    listener(this.prices);
    return () => this.listeners.delete(listener);
  }

  // Get current price for a symbol
  getPrice(symbol: string): SymbolPrice | undefined {
    return this.prices.get(symbol);
  }

  // Get all prices
  getAllPrices(): Map<string, SymbolPrice> {
    return new Map(this.prices);
  }

  private notifyListeners() {
    const pricesCopy = new Map(this.prices);
    this.listeners.forEach((listener) => {
      try {
        listener(pricesCopy);
      } catch (e) {
        console.error('Price listener error:', e);
      }
    });
  }

  // Reset daily prices (call at start of new trading day)
  resetDailyPrices() {
    this.dailyOpenPrices.clear();
    this.dailyVolumes.clear();
    this.initialized.clear();
  }
}

// Singleton instance
export const priceStore = new PriceStore();
