import { render, screen } from '@testing-library/react';
import { expect, test } from 'vitest';
import App from './App';

test('deve renderizar o título do portal SUS', () => {
  render(<App />);
  const titleElement = screen.getByText(/SUS Blockchain/i);
  expect(titleElement).toBeInTheDocument();
});

test('deve mostrar o botão de acesso', () => {
  render(<App />);
  const loginButton = screen.getByText(/ACESSO/i);
  expect(loginButton).toBeInTheDocument();
});
