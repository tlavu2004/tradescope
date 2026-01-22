// Shared price store - singleton that manages real-time price data for all symbols
// This centralizes WebSocket subscriptions to avoid duplicates

import { sharedWs } from './sharedWs';

export interface SymbolPrice {
  symbol: string;
  price: number;
  open: number;
  high: number;
  low: number;
  close: number;
  change: number;
  changePercent: number;
  volume: number;
  lastUpdate: number;
}

type PriceListener = (prices: Map<string, SymbolPrice>) => void;

class PriceStore {
  private prices: Map<string, SymbolPrice> = new Map();
  private listeners: Set<PriceListener> = new Set();
  private subscriptions: Map<string, () => void> = new Map();
  private openPrices: Map<string, number> = new Map();

  // Subscribe to a symbol's price updates
  subscribe(symbol: string, interval: string = '1m') {
    const key = `${symbol}:${interval}`;
    if (this.subscriptions.has(key)) {
      return; // Already subscribed
    }

    const handler = (candle: any) => {
      const closePrice = Number(candle.close);
      const openPrice = Number(candle.open);
      const volume = Number(candle.volume) || 0;

      // Store open price for change calculation (first candle's open)
      if (!this.openPrices.has(symbol)) {
        this.openPrices.set(symbol, openPrice);
      }

      const storedOpen = this.openPrices.get(symbol) || openPrice;
      const change = closePrice - storedOpen;
      const changePercent = storedOpen > 0 ? (change / storedOpen) * 100 : 0;

      const priceData: SymbolPrice = {
        symbol,
        price: closePrice,
        open: openPrice,
        high: Number(candle.high),
        low: Number(candle.low),
        close: closePrice,
        change,
        changePercent,
        volume,
        lastUpdate: Date.now(),
      };

      this.prices.set(symbol, priceData);
      this.notifyListeners();
    };

    const unsubscribe = sharedWs.subscribe(symbol, handler, interval);
    this.subscriptions.set(key, unsubscribe);
  }

  // Unsubscribe from a symbol
  unsubscribe(symbol: string, interval: string = '1m') {
    const key = `${symbol}:${interval}`;
    const unsub = this.subscriptions.get(key);
    if (unsub) {
      unsub();
      this.subscriptions.delete(key);
    }
  }

  // Subscribe multiple symbols at once
  subscribeAll(symbols: string[], interval: string = '1m') {
    symbols.forEach((sym) => this.subscribe(sym, interval));
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

  // Reset open prices (call at start of new trading day)
  resetOpenPrices() {
    this.openPrices.clear();
  }
}

// Singleton instance
export const priceStore = new PriceStore();
