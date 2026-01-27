import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ChatComponent from '@/components/ChatComponent';

// Mock the AuthContext
const mockAuthFetch = vi.fn();

vi.mock('@/context/AuthContext', () => ({
  useAuth: () => ({
    authFetch: mockAuthFetch,
  }),
}));

// Mock chat texts
vi.mock('@/constants/text', () => ({
  chatTexts: {
    headerTitle: 'LLM Assistant',
    inputPlaceholder: 'Input your message...',
    sendButton: 'Send',
    connectionError: 'Connection Failed.',
  },
}));

describe('ChatComponent', () => {
  beforeEach(() => {
    vi.clearAllMocks();

    // Default mock implementation for streaming
    mockAuthFetch.mockImplementation(async () => {
      const encoder = new TextEncoder();
      const stream = new ReadableStream({
        async start(controller) {
          controller.enqueue(encoder.encode('Hello, '));
          controller.enqueue(encoder.encode('this is a test response.'));
          controller.close();
        },
      });

      return {
        body: stream,
      };
    });
  });

  it('should render chat bubble button', () => {
    render(<ChatComponent />);

    // The chat bubble button should be visible initially
    const buttons = screen.getAllByRole('button');
    expect(buttons.length).toBeGreaterThan(0);
  });

  it('should open chat window when bubble is clicked', async () => {
    const user = userEvent.setup();
    render(<ChatComponent />);

    // Find and click the chat bubble (the last button which is the bubble)
    const buttons = screen.getAllByRole('button');
    const chatBubble = buttons[buttons.length - 1];
    await user.click(chatBubble);

    expect(screen.getByText('LLM Assistant')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Input your message...')).toBeInTheDocument();
  });

  it('should close chat window when close button is clicked', async () => {
    const user = userEvent.setup();
    render(<ChatComponent />);

    // Open chat
    const buttons = screen.getAllByRole('button');
    const chatBubble = buttons[buttons.length - 1];
    await user.click(chatBubble);

    // Find and click close button
    const closeButton = screen.getByText('×');
    await user.click(closeButton);

    // Chat window should have pointer-events-none class (closed state)
    const chatWindow = screen.getByText('LLM Assistant').closest('div[class*="w-[370px]"]');
    expect(chatWindow).toHaveClass('pointer-events-none');
  });

  it('should not submit empty messages', async () => {
    const user = userEvent.setup();
    render(<ChatComponent />);

    // Open chat
    const buttons = screen.getAllByRole('button');
    const chatBubble = buttons[buttons.length - 1];
    await user.click(chatBubble);

    // Try to submit empty message
    const sendButton = screen.getByRole('button', { name: 'Send' });
    await user.click(sendButton);

    expect(mockAuthFetch).not.toHaveBeenCalled();
  });

  it('should send message and display user message', async () => {
    const user = userEvent.setup();
    render(<ChatComponent />);

    // Open chat
    const buttons = screen.getAllByRole('button');
    const chatBubble = buttons[buttons.length - 1];
    await user.click(chatBubble);

    // Type message
    const input = screen.getByPlaceholderText('Input your message...');
    await user.type(input, 'Hello AI');

    // Submit message
    const sendButton = screen.getByRole('button', { name: 'Send' });
    await user.click(sendButton);

    // User message should appear
    expect(screen.getByText('Hello AI')).toBeInTheDocument();
  });

  it('should display streaming response', async () => {
    const user = userEvent.setup();
    render(<ChatComponent />);

    // Open chat
    const buttons = screen.getAllByRole('button');
    const chatBubble = buttons[buttons.length - 1];
    await user.click(chatBubble);

    // Type and send message
    const input = screen.getByPlaceholderText('Input your message...');
    await user.type(input, 'Hello');

    const sendButton = screen.getByRole('button', { name: 'Send' });
    await user.click(sendButton);

    // Wait for streaming response
    await waitFor(() => {
      expect(screen.getByText(/this is a test response/)).toBeInTheDocument();
    });
  });

  it('should handle connection error', async () => {
    mockAuthFetch.mockRejectedValue(new Error('Network error'));

    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    const user = userEvent.setup();
    render(<ChatComponent />);

    // Open chat
    const buttons = screen.getAllByRole('button');
    const chatBubble = buttons[buttons.length - 1];
    await user.click(chatBubble);

    // Type and send message
    const input = screen.getByPlaceholderText('Input your message...');
    await user.type(input, 'Hello');

    const sendButton = screen.getByRole('button', { name: 'Send' });
    await user.click(sendButton);

    // Wait for error message
    await waitFor(() => {
      expect(screen.getByText('Connection Failed.')).toBeInTheDocument();
    });

    consoleSpy.mockRestore();
  });

  it('should clear input after sending message', async () => {
    const user = userEvent.setup();
    render(<ChatComponent />);

    // Open chat
    const buttons = screen.getAllByRole('button');
    const chatBubble = buttons[buttons.length - 1];
    await user.click(chatBubble);

    // Type and send message
    const input = screen.getByPlaceholderText('Input your message...') as HTMLInputElement;
    await user.type(input, 'Hello');
    expect(input.value).toBe('Hello');

    const sendButton = screen.getByRole('button', { name: 'Send' });
    await user.click(sendButton);

    // Input should be cleared
    expect(input.value).toBe('');
  });

  it('should submit on form submit', async () => {
    const user = userEvent.setup();
    render(<ChatComponent />);

    // Open chat
    const buttons = screen.getAllByRole('button');
    const chatBubble = buttons[buttons.length - 1];
    await user.click(chatBubble);

    // Type message
    const input = screen.getByPlaceholderText('Input your message...');
    await user.type(input, 'Test message{enter}');

    // Should have called authFetch
    expect(mockAuthFetch).toHaveBeenCalledWith('/api/chat', {
      method: 'POST',
      body: JSON.stringify({ prompt: 'Test message' }),
    });
  });

  it('should handle missing response body', async () => {
    mockAuthFetch.mockResolvedValue({ body: null });

    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    const user = userEvent.setup();
    render(<ChatComponent />);

    // Open chat
    const buttons = screen.getAllByRole('button');
    const chatBubble = buttons[buttons.length - 1];
    await user.click(chatBubble);

    // Type and send message
    const input = screen.getByPlaceholderText('Input your message...');
    await user.type(input, 'Hello');

    const sendButton = screen.getByRole('button', { name: 'Send' });
    await user.click(sendButton);

    // Wait for error handling
    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalled();
    });

    consoleSpy.mockRestore();
  });
});
