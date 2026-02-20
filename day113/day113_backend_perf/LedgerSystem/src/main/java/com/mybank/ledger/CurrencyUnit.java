package com.mybank.ledger;

import java.util.Arrays;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.function.Function;
import java.util.stream.Collectors;

/**
 * Represents a specific currency with its ISO code and default fraction digits.
 * Implemented as an immutable class for robustness.
 */
public final class CurrencyUnit {
    private final String code;
    private final int defaultFractionDigits;

    // Pre-defined common currencies
    public static final CurrencyUnit USD = new CurrencyUnit("USD", 2);
    public static final CurrencyUnit EUR = new CurrencyUnit("EUR", 2);
    public static final CurrencyUnit JPY = new CurrencyUnit("JPY", 0);
    public static final CurrencyUnit BTC = new CurrencyUnit("BTC", 8); // Bitcoin, 8 decimal places (Satoshis)

    private static final Map<String, CurrencyUnit> CURRENCIES_BY_CODE = 
        Arrays.asList(USD, EUR, JPY, BTC)
              .stream()
              .collect(Collectors.toMap(CurrencyUnit::getCode, Function.identity()));

    private CurrencyUnit(String code, int defaultFractionDigits) {
        if (code == null || code.trim().isEmpty()) {
            throw new IllegalArgumentException("Currency code cannot be null or empty.");
        }
        if (defaultFractionDigits < 0) {
            throw new IllegalArgumentException("Default fraction digits cannot be negative.");
        }
        this.code = code.toUpperCase();
        this.defaultFractionDigits = defaultFractionDigits;
    }

    /**
     * Factory method to get a CurrencyUnit instance by its ISO code.
     * For simplicity, this only supports pre-defined currencies.
     */
    public static CurrencyUnit of(String code) {
        return Optional.ofNullable(CURRENCIES_BY_CODE.get(code.toUpperCase()))
                       .orElseThrow(() -> new IllegalArgumentException("Unsupported currency code: " + code));
    }

    public String getCode() {
        return code;
    }

    public int getDefaultFractionDigits() {
        return defaultFractionDigits;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        CurrencyUnit that = (CurrencyUnit) o;
        return defaultFractionDigits == that.defaultFractionDigits && Objects.equals(code, that.code);
    }

    @Override
    public int hashCode() {
        return Objects.hash(code, defaultFractionDigits);
    }

    @Override
    public String toString() {
        return code;
    }
}
