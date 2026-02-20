package com.mybank.ledger;

import org.junit.Test;
import java.math.BigDecimal;
import static org.junit.Assert.*;

public class MoneyTest {

    @Test
    public void testAddSameCurrency() {
        Money a = Money.of(new BigDecimal("10.00"), CurrencyUnit.USD);
        Money b = Money.of(new BigDecimal("5.50"), CurrencyUnit.USD);
        Money sum = a.add(b);
        assertEquals(1550L, sum.getMinorUnits());
        assertEquals(CurrencyUnit.USD, sum.getCurrencyUnit());
    }

    @Test
    public void testSubtractSameCurrency() {
        Money a = Money.of(new BigDecimal("10.00"), CurrencyUnit.USD);
        Money b = Money.of(new BigDecimal("3.25"), CurrencyUnit.USD);
        Money diff = a.subtract(b);
        assertEquals(675L, diff.getMinorUnits());
    }

    @Test(expected = IllegalArgumentException.class)
    public void testAddDifferentCurrenciesThrows() {
        Money usd = Money.of(BigDecimal.ONE, CurrencyUnit.USD);
        Money eur = Money.of(BigDecimal.ONE, CurrencyUnit.EUR);
        usd.add(eur);
    }
}
