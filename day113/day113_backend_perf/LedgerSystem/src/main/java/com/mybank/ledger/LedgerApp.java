package com.mybank.ledger;

import java.math.BigDecimal;
import java.util.HashMap;
import java.util.Map;

public class LedgerApp {

    // Simple in-memory ledger for demonstration
    private static final Map<String, Money> accountBalances = new HashMap<>();

    public static void main(String[] args) {
        System.out.println("----------------------------------------------");
        System.out.println("  MyBank Ledger System - Day 6: Currency & Scaling Units ");
        System.out.println("----------------------------------------------");

        // Initialize accounts
        initializeAccount("Alice", CurrencyUnit.USD, new BigDecimal("1000.00"));
        initializeAccount("Bob", CurrencyUnit.EUR, new BigDecimal("500.50"));
        initializeAccount("Charlie", CurrencyUnit.JPY, new BigDecimal("12345")); // JPY has 0 fraction digits
        initializeAccount("David", CurrencyUnit.BTC, new BigDecimal("0.51234567")); // BTC with 8 fraction digits

        displayBalances();

        // --- Demo Transactions ---
        System.out.println("\n--- Processing Transactions ---");

        // 1. Valid Deposit (USD)
        processTransaction("Alice", Money.of(new BigDecimal("250.75"), CurrencyUnit.USD), "deposit");

        // 2. Valid Withdrawal (EUR)
        processTransaction("Bob", Money.of(new BigDecimal("100.25"), CurrencyUnit.EUR), "withdraw");

        // 3. Attempt to add different currencies (should fail)
        System.out.println("\nAttempting invalid transaction: Alice tries to deposit EUR into USD account...");
        try {
            processTransaction("Alice", Money.of(new BigDecimal("50.00"), CurrencyUnit.EUR), "deposit");
        } catch (IllegalArgumentException e) {
            System.out.println("  -> ERROR: " + e.getMessage());
        }

        // 4. Valid Deposit (JPY)
        processTransaction("Charlie", Money.of(new BigDecimal("5000"), CurrencyUnit.JPY), "deposit");

        // 5. Valid Withdrawal (BTC)
        processTransaction("David", Money.of(new BigDecimal("0.12345678"), CurrencyUnit.BTC), "withdraw");
        processTransaction("David", Money.of(new BigDecimal("0.00000001"), CurrencyUnit.BTC), "withdraw"); // Smallest unit

        // 6. Attempt insufficient funds (USD)
        System.out.println("\nAttempting invalid transaction: Alice tries to withdraw too much USD...");
        try {
            processTransaction("Alice", Money.of(new BigDecimal("2000.00"), CurrencyUnit.USD), "withdraw");
        } catch (IllegalStateException e) {
            System.out.println("  -> ERROR: " + e.getMessage());
        }

        displayBalances();

        System.out.println("\n----------------------------------------------");
        System.out.println("  Ledger System Demo Complete. ");
        System.out.println("----------------------------------------------");
    }

    private static void initializeAccount(String accountName, CurrencyUnit currency, BigDecimal initialAmount) {
        Money initialMoney = Money.of(initialAmount, currency);
        accountBalances.put(accountName, initialMoney);
        System.out.printf("Initialized account '%s' with %s%n", accountName, initialMoney.toString());
    }

    private static void processTransaction(String accountName, Money transactionAmount, String type) {
        System.out.printf("Processing %s for '%s': %s%n", type, accountName, transactionAmount.toString());
        Money currentBalance = accountBalances.get(accountName);

        if (currentBalance == null) {
            System.out.println("  -> ERROR: Account not found: " + accountName);
            return;
        }

        if (!currentBalance.isSameCurrency(transactionAmount)) {
            throw new IllegalArgumentException(
                String.format("Transaction currency (%s) does not match account currency (%s) for account '%s'.",
                    transactionAmount.getCurrencyUnit().getCode(), currentBalance.getCurrencyUnit().getCode(), accountName));
        }

        Money newBalance;
        if ("deposit".equalsIgnoreCase(type)) {
            newBalance = currentBalance.add(transactionAmount);
        } else if ("withdraw".equalsIgnoreCase(type)) {
            if (!currentBalance.greaterThanOrEqual(transactionAmount)) {
                throw new IllegalStateException(
                    String.format("Insufficient funds for account '%s'. Current: %s, Attempted withdrawal: %s",
                        accountName, currentBalance.toString(), transactionAmount.toString()));
            }
            newBalance = currentBalance.subtract(transactionAmount);
        } else {
            System.out.println("  -> ERROR: Invalid transaction type: " + type);
            return;
        }

        accountBalances.put(accountName, newBalance);
        System.out.printf("  -> Success! New balance for '%s': %s%n", accountName, newBalance.toString());
    }

    private static void displayBalances() {
        System.out.println("\n--- Current Account Balances ---");
        if (accountBalances.isEmpty()) {
            System.out.println("  No accounts found.");
            return;
        }
        accountBalances.forEach((name, balance) -> System.out.printf("  %-10s: %s%n", name, balance.toString()));
        System.out.println("--------------------------------");
    }
}
