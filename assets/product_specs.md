# Product Specifications - E-Shop Checkout

## Discount Codes
- **SAVE15**: Applies a 15% discount to the total cart value.
- **FREESHIP**: Makes shipping free (if Express is selected, it overrides the cost). *Note: This is a hidden feature not fully implemented in UI but good for testing edge cases.*

## Shipping Rules
- **Standard Shipping**: Free (0$). Delivery in 5-7 business days.
- **Express Shipping**: Costs $10 flat rate. Delivery in 1-2 business days.

## Cart Limits
- Maximum 5 items of the same type allowed (e.g., max 5 Headphones).
- Minimum order value for checkout is $0 (no minimum).

## Payment Methods
- **Credit Card**: Requires valid card number (simulated).
- **PayPal**: Redirects to PayPal login (simulated).
