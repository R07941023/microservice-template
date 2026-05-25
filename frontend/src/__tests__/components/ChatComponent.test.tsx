import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ChatComponent from '@/components/ChatComponent';

// Mock useAuth
vi.mock('@/context/AuthContext', () => ({
  useAuth: () => ({
    token: 'mock-token',
    refreshToken: vi.fn(),
    authFetch: vi.fn(),
  }),
}));

// Mock useChat from @ai-sdk/react
const mockSendMessage = vi.fn();
const mockStop = vi.fn();
let mockMessages: { id: string; role: string; parts: { type: string; text: string }[] }[] = [];
let mockStatus = 'ready';

vi.mock('@ai-sdk/react', () => ({
  useChat: () => ({
    messages: mockMessages,
    sendMessage: mockSendMessage,
    status: mockStatus,
    stop: mockStop,
  }),
}));

// Mock next/image
vi.mock('next/image', () => ({
  // eslint-disable-next-line @next/next/no-img-element
  default: ({ alt }: { alt: string }) => <img alt={alt} />,
}));

describe('ChatComponent', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockMessages = [];
    mockStatus = 'ready';
  });

  it('should render chat bubble button', () => {
    render(<ChatComponent />);
    const buttons = screen.getAllByRole('button');
    expect(buttons.length).toBeGreaterThan(0);
  });

  it('should open chat window when bubble is clicked', async () => {
    const user = userEvent.setup();
    render(<ChatComponent />);

    const buttons = screen.getAllByRole('button');
    const chatBubble = buttons[buttons.length - 1];
    await user.click(chatBubble);

    expect(screen.getByText('MapleAI')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Ask a question...')).toBeInTheDocument();
  });

  it('should close chat window when close button is clicked', async () => {
    const user = userEvent.setup();
    const { container } = render(<ChatComponent />);

    const buttons = screen.getAllByRole('button');
    const chatBubble = buttons[buttons.length - 1];
    await user.click(chatBubble);

    // Close button is the first button inside the header (border-b section)
    const header = container.querySelector('.border-b.border-gray-200') as HTMLElement;
    const closeButton = within(header).getByRole('button');
    await user.click(closeButton);

    const chatWindow = screen.getByText('MapleAI').closest('div[class*="w-[700px]"]');
    expect(chatWindow).toHaveClass('pointer-events-none');
  });

  it('should not submit empty messages', async () => {
    const user = userEvent.setup();
    render(<ChatComponent />);

    const buttons = screen.getAllByRole('button');
    const chatBubble = buttons[buttons.length - 1];
    await user.click(chatBubble);

    // Press Enter with empty input — handler guards against empty submit
    await user.keyboard('{Enter}');

    expect(mockSendMessage).not.toHaveBeenCalled();
  });

  it('should send message when submitted', async () => {
    const user = userEvent.setup();
    render(<ChatComponent />);

    const buttons = screen.getAllByRole('button');
    const chatBubble = buttons[buttons.length - 1];
    await user.click(chatBubble);

    const input = screen.getByPlaceholderText('Ask a question...');
    await user.type(input, 'Hello AI');

    await user.keyboard('{Enter}');

    expect(mockSendMessage).toHaveBeenCalledWith({ text: 'Hello AI' });
  });

  it('should display messages from useChat', async () => {
    mockMessages = [
      { id: '1', role: 'user', parts: [{ type: 'text', text: 'Hello' }] },
      { id: '2', role: 'assistant', parts: [{ type: 'text', text: 'Hi there!' }] },
    ];

    render(<ChatComponent />);

    const buttons = screen.getAllByRole('button');
    await userEvent.setup().click(buttons[buttons.length - 1]);

    expect(screen.getByText('Hello')).toBeInTheDocument();
    expect(screen.getByText('Hi there!')).toBeInTheDocument();
  });

  it('should clear input after sending message', async () => {
    const user = userEvent.setup();
    render(<ChatComponent />);

    const buttons = screen.getAllByRole('button');
    await user.click(buttons[buttons.length - 1]);

    const input = screen.getByPlaceholderText('Ask a question...') as HTMLInputElement;
    await user.type(input, 'Hello');
    expect(input.value).toBe('Hello');

    await user.keyboard('{Enter}');

    expect(input.value).toBe('');
  });

  it('should show loading state when streaming', async () => {
    mockStatus = 'streaming';
    render(<ChatComponent />);

    const buttons = screen.getAllByRole('button');
    await userEvent.setup().click(buttons[buttons.length - 1]);

    // Loading dots should be visible
    const dots = document.querySelectorAll('.animate-bounce');
    expect(dots.length).toBeGreaterThan(0);
  });

  it('should render without crashing with mocked useChat', async () => {
    render(<ChatComponent />);
    // Component renders with the useChat mock without throwing
    expect(screen.getAllByRole('button').length).toBeGreaterThan(0);
  });
});
