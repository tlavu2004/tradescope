/**
 * WebSocket Stress Test Script for STOMP over SockJS
 * 
 * Usage: node ws-stress-test.js [numClients] [wsUrl]
 * Example: node ws-stress-test.js 1000 http://localhost/ws
 */

const SockJS = require('sockjs-client');
const Stomp = require('@stomp/stompjs');

// Configuration
const DEFAULT_NUM_CLIENTS = 1000;
const DEFAULT_WS_URL = 'http://localhost/ws';
const CONNECT_DELAY_MS = 10; // Delay between each connection to avoid burst
const TEST_DURATION_MS = 60000; // Run test for 60 seconds
const SUBSCRIBE_TOPIC = '/topic/candle.BTCUSDT.1m';

// Parse arguments
const numClients = parseInt(process.argv[2]) || DEFAULT_NUM_CLIENTS;
const wsUrl = process.argv[3] || DEFAULT_WS_URL;

// Stats
let stats = {
  attempted: 0,
  connected: 0,
  failed: 0,
  messagesReceived: 0,
  disconnected: 0,
  errors: [],
  connectTimes: [],
};

class TestClient {
  constructor(id) {
    this.id = id;
    this.client = null;
    this.connected = false;
    this.startTime = null;
  }

  connect() {
    return new Promise((resolve) => {
      this.startTime = Date.now();
      stats.attempted++;

      try {
        this.client = new Stomp.Client({
          webSocketFactory: () => new SockJS(wsUrl),
          reconnectDelay: 0, // Disable auto-reconnect for testing
          debug: () => { }, // Disable debug logs
          onConnect: () => {
            const connectTime = Date.now() - this.startTime;
            stats.connected++;
            stats.connectTimes.push(connectTime);
            this.connected = true;

            // Subscribe to topic
            this.client.subscribe(SUBSCRIBE_TOPIC, (message) => {
              stats.messagesReceived++;
            });

            resolve(true);
          },
          onDisconnect: () => {
            if (this.connected) {
              stats.disconnected++;
              this.connected = false;
            }
          },
          onStompError: (frame) => {
            stats.failed++;
            stats.errors.push(`Client ${this.id}: ${frame.headers['message']}`);
            resolve(false);
          },
          onWebSocketError: (event) => {
            stats.failed++;
            stats.errors.push(`Client ${this.id}: WebSocket error`);
            resolve(false);
          },
        });

        this.client.activate();

        // Timeout after 10 seconds
        setTimeout(() => {
          if (!this.connected) {
            stats.failed++;
            stats.errors.push(`Client ${this.id}: Connection timeout`);
            resolve(false);
          }
        }, 10000);
      } catch (e) {
        stats.failed++;
        stats.errors.push(`Client ${this.id}: ${e.message}`);
        resolve(false);
      }
    });
  }

  disconnect() {
    if (this.client && this.connected) {
      this.client.deactivate();
    }
  }
}

async function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function printStats() {
  const avgConnectTime = stats.connectTimes.length > 0
    ? (stats.connectTimes.reduce((a, b) => a + b, 0) / stats.connectTimes.length).toFixed(2)
    : 0;

  console.log('\n========== WebSocket Stress Test Results ==========');
  console.log(`Target URL: ${wsUrl}`);
  console.log(`Target Clients: ${numClients}`);
  console.log('');
  console.log(`✅ Connected:   ${stats.connected}`);
  console.log(`❌ Failed:      ${stats.failed}`);
  console.log(`📨 Messages:    ${stats.messagesReceived}`);
  console.log(`🔌 Disconnected: ${stats.disconnected}`);
  console.log(`⏱️  Avg Connect: ${avgConnectTime}ms`);
  console.log('');

  const successRate = ((stats.connected / stats.attempted) * 100).toFixed(2);
  console.log(`📊 Success Rate: ${successRate}%`);

  if (stats.errors.length > 0) {
    console.log('\n⚠️  First 10 errors:');
    stats.errors.slice(0, 10).forEach((e) => console.log(`   - ${e}`));
  }

  console.log('===================================================\n');
}

async function runTest() {
  console.log(`\n🚀 Starting WebSocket Stress Test`);
  console.log(`   URL: ${wsUrl}`);
  console.log(`   Clients: ${numClients}`);
  console.log(`   Topic: ${SUBSCRIBE_TOPIC}\n`);

  const clients = [];

  // Create and connect clients with delay
  for (let i = 0; i < numClients; i++) {
    const client = new TestClient(i);
    clients.push(client);

    // Don't await - connect in parallel with small delay
    client.connect();

    if (i % 100 === 0) {
      console.log(`   Connecting clients: ${i}/${numClients}`);
    }

    await sleep(CONNECT_DELAY_MS);
  }

  console.log(`   All connection attempts initiated, waiting for results...`);

  // Wait for connections to establish
  await sleep(15000);

  // Print intermediate stats
  console.log(`\n📊 After connection phase:`);
  printStats();

  // Keep test running to receive messages
  console.log(`⏳ Running for ${TEST_DURATION_MS / 1000}s to collect messages...`);
  await sleep(TEST_DURATION_MS);

  // Final stats
  console.log(`\n📊 Final results after ${TEST_DURATION_MS / 1000}s:`);
  printStats();

  // Cleanup
  console.log('🧹 Disconnecting clients...');
  clients.forEach((c) => c.disconnect());

  await sleep(2000);
  console.log('✅ Test complete!\n');

  process.exit(0);
}

// Run the test
runTest().catch((e) => {
  console.error('Test failed:', e);
  process.exit(1);
});
