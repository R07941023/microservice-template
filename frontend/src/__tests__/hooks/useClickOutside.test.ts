import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook } from '@testing-library/react';
import { useRef } from 'react';
import { useClickOutside } from '@/hooks/useClickOutside';

describe('useClickOutside', () => {
  let handler: ReturnType<typeof vi.fn>;
  let container: HTMLDivElement;
  let outsideElement: HTMLDivElement;

  beforeEach(() => {
    handler = vi.fn();
    container = document.createElement('div');
    container.setAttribute('data-testid', 'inside');
    outsideElement = document.createElement('div');
    outsideElement.setAttribute('data-testid', 'outside');
    document.body.appendChild(container);
    document.body.appendChild(outsideElement);
  });

  afterEach(() => {
    document.body.removeChild(container);
    document.body.removeChild(outsideElement);
  });

  it('should call handler when clicking outside the ref element', () => {
    const TestWrapper = () => {
      const ref = useRef<HTMLDivElement>(container);
      useClickOutside(ref, handler);
      return null;
    };

    renderHook(() => TestWrapper());

    // Click outside
    outsideElement.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }));

    expect(handler).toHaveBeenCalledTimes(1);
  });

  it('should not call handler when clicking inside the ref element', () => {
    const TestWrapper = () => {
      const ref = useRef<HTMLDivElement>(container);
      useClickOutside(ref, handler);
      return null;
    };

    renderHook(() => TestWrapper());

    // Click inside
    container.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }));

    expect(handler).not.toHaveBeenCalled();
  });

  it('should handle touch events', () => {
    const TestWrapper = () => {
      const ref = useRef<HTMLDivElement>(container);
      useClickOutside(ref, handler);
      return null;
    };

    renderHook(() => TestWrapper());

    // Touch outside
    outsideElement.dispatchEvent(new TouchEvent('touchstart', { bubbles: true }));

    expect(handler).toHaveBeenCalledTimes(1);
  });

  it('should not call handler when clicking on descendant elements', () => {
    const childElement = document.createElement('span');
    container.appendChild(childElement);

    const TestWrapper = () => {
      const ref = useRef<HTMLDivElement>(container);
      useClickOutside(ref, handler);
      return null;
    };

    renderHook(() => TestWrapper());

    // Click on child element
    childElement.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }));

    expect(handler).not.toHaveBeenCalled();
  });

  it('should handle null ref gracefully', () => {
    const TestWrapper = () => {
      const ref = useRef<HTMLDivElement>(null);
      useClickOutside(ref, handler);
      return null;
    };

    renderHook(() => TestWrapper());

    // Click anywhere - should not crash
    outsideElement.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }));

    // Handler should not be called when ref is null
    expect(handler).not.toHaveBeenCalled();
  });

  it('should cleanup event listeners on unmount', () => {
    const removeEventListenerSpy = vi.spyOn(document, 'removeEventListener');

    const TestWrapper = () => {
      const ref = useRef<HTMLDivElement>(container);
      useClickOutside(ref, handler);
      return null;
    };

    const { unmount } = renderHook(() => TestWrapper());

    unmount();

    expect(removeEventListenerSpy).toHaveBeenCalledWith('mousedown', expect.any(Function));
    expect(removeEventListenerSpy).toHaveBeenCalledWith('touchstart', expect.any(Function));

    removeEventListenerSpy.mockRestore();
  });
});
