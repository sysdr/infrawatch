package com.mybank.ledger;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.Objects;

/**
 * Represents an immutable monetary amount, internally stored as a long
 * representing minor units to ensure precision and performance.
 * It's strongly typed with a CurrencyUnit to prevent currency mixing.
 */
public final class Money implements Comparable<Money> {

    private final long minorUnits; // Amount in the smallest indivisible unit (e.g., cents for USD)
    private final CurrencyUnit currencyUnit;

    // Private constructor to enforce creation via static factory methods
    private Money(long minorUnits, CurrencyUnit currencyUnit) {
        Objects.requireNonNull(currencyUnit, "CurrencyUnit cannot be null.");
        this.minorUnits = minorUnits;
        this.currencyUnit = currencyUnit;
    }

    /**
     * Creates a Money instance from a BigDecimal amount and a CurrencyUnit.
     * The BigDecimal is scaled and rounded to the minor units.
     *
     * @param amount       The monetary amount as BigDecimal.
     * @param currencyUnit The currency.
     * @return An immutable Money instance.
     * @throws IllegalArgumentException if currencyUnit is null.
     */
    public static Money of(BigDecimal amount, CurrencyUnit currencyUnit) {
        Objects.requireNonNull(amount, "Amount cannot be null.");
        Objects.requireNonNull(currencyUnit, "CurrencyUnit cannot be null.");

        // Scale the BigDecimal to the currency's default fraction digits and convert to minor units
        BigDecimal scaledAmount = amount.setScale(currencyUnit.getDefaultFractionDigits(), RoundingMode.HALF_EVEN);
        long minorUnits = scaledAmount.movePointRight(currencyUnit.getDefaultFractionDigits()).longValueExact(); // Ensure no fractional minor units
        
        return new Money(minorUnits, currencyUnit);
    }

    /**
     * Creates a zero-value Money instance for a given currency.
     */
    public static Money zero(CurrencyUnit currencyUnit) {
        return new Money(0, currencyUnit);
    }

    public long getMinorUnits() {
        return minorUnits;
    }

    public CurrencyUnit getCurrencyUnit() {
        return currencyUnit;
    }

    /**
     * Converts the internal minor units representation back to a BigDecimal.
     *
     * @return The monetary amount as BigDecimal.
     */
    public BigDecimal toBigDecimal() {
        return BigDecimal.valueOf(minorUnits)
                         .movePointLeft(currencyUnit.getDefaultFractionDigits())
                         .setScale(currencyUnit.getDefaultFractionDigits(), RoundingMode.UNNECESSARY);
    }

    /**
     * Adds another Money instance to this one. Currencies must match.
     *
     * @param other The Money instance to add.
     * @return A new Money instance representing the sum.
     * @throws IllegalArgumentException if currencies do not match or if overflow occurs.
     */
    public Money add(Money other) {
        if (!isSameCurrency(other)) {
            throw new IllegalArgumentException("Cannot add different currencies: " + this.currencyUnit + " and " + other.currencyUnit);
        }
        long resultMinorUnits = Math.addExact(this.minorUnits, other.minorUnits); // Throws ArithmeticException on overflow
        return new Money(resultMinorUnits, this.currencyUnit);
    }

    /**
     * Subtracts another Money instance from this one. Currencies must match.
     *
     * @param other The Money instance to subtract.
     * @return A new Money instance representing the difference.
     * @throws IllegalArgumentException if currencies do not match or if overflow occurs.
     */
    public Money subtract(Money other) {
        if (!isSameCurrency(other)) {
            throw new IllegalArgumentException("Cannot subtract different currencies: " + this.currencyUnit + " and " + other.currencyUnit);
        }
        long resultMinorUnits = Math.subtractExact(this.minorUnits, other.minorUnits); // Throws ArithmeticException on overflow
        return new Money(resultMinorUnits, this.currencyUnit);
    }

    /**
     * Checks if this Money instance has the same currency as another.
     *
     * @param other The other Money instance.
     * @return true if currencies are the same, false otherwise.
     */
    public boolean isSameCurrency(Money other) {
        return this.currencyUnit.equals(other.currencyUnit);
    }

    /**
     * Checks if this Money instance is greater than or equal to another.
     * Currencies must match.
     */
    public boolean greaterThanOrEqual(Money other) {
        if (!isSameCurrency(other)) {
            throw new IllegalArgumentException("Cannot compare different currencies: " + this.currencyUnit + " and " + other.currencyUnit);
        }
        return this.minorUnits >= other.minorUnits;
    }

    /**
     * Checks if this Money instance is strictly greater than another.
     * Currencies must match.
     */
    public boolean greaterThan(Money other) {
        if (!isSameCurrency(other)) {
            throw new IllegalArgumentException("Cannot compare different currencies: " + this.currencyUnit + " and " + other.currencyUnit);
        }
        return this.minorUnits > other.minorUnits;
    }

    @Override
    public int compareTo(Money other) {
        if (!isSameCurrency(other)) {
            throw new IllegalArgumentException("Cannot compare different currencies: " + this.currencyUnit + " and " + other.currencyUnit);
        }
        return Long.compare(this.minorUnits, other.minorUnits);
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Money money = (Money) o;
        return minorUnits == money.minorUnits && Objects.equals(currencyUnit, money.currencyUnit);
    }

    @Override
    public int hashCode() {
        return Objects.hash(minorUnits, currencyUnit);
    }

    @Override
    public String toString() {
        return String.format("%s %.2f", currencyUnit.getCode(), toBigDecimal());
    }
}
