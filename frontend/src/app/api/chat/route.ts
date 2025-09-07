import { NextResponse } from 'next/server';

// Helper function to create a delay
function sleep(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// This function simulates a streaming response from an LLM.
export async function POST() {
  const text = "這是一個來自後端的模擬流式回應。透過這種方式，我們可以先專注於前端的數據流處理和 UI 呈現，而無需等待真實後端的完成。";
  const chunks = text.split('');

  const stream = new ReadableStream({
    async start(controller) {
      const encoder = new TextEncoder();
      for (const chunk of chunks) {
        controller.enqueue(encoder.encode(chunk));
        await sleep(50); // Simulate a delay for each token
      }
      controller.close();
    },
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/plain; charset=utf-8',
    },
  });
}
