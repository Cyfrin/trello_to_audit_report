
| Finding                                                                             | Severity | Status   |
| :-----------------------------------------------------------------------------------| :------- | :------- |
| [H-1 [H-03] removeLiquidity logic is wrong for non-linear Constant Function AMMs](h-1-h-03-removeliquidity-logic-is-wrong-for-non-linear-constant-function-amms) |H| Open |
| [L-1 The event `Swap` in transfer should go after the external token call](l-1-the-event-`swap`-in-transfer-should-go-after-the-external-token-call) |L| Open |

## [H-1] [H-03] removeLiquidity logic is wrong for non-linear Constant Function AMMs
[https://github.com/BeanstalkFarms/Wells/blob/7c498215f843620cb24ec5bbf978c6495f6e5fe4/src/Well.sol#L308](https://github.com/BeanstalkFarms/Wells/blob/7c498215f843620cb24ec5bbf978c6495f6e5fe4/src/Well.sol#L308 "smartCard-inline")

[https://github.com/BeanstalkFarms/Wells/blob/7c498215f843620cb24ec5bbf978c6495f6e5fe4/src/Well.sol#L335](https://github.com/BeanstalkFarms/Wells/blob/7c498215f843620cb24ec5bbf978c6495f6e5fe4/src/Well.sol#L335 "smartCard-inline")

The current implementation of `removeLiquidity()` and `getRemoveLiquidityOut()` assumes variable-wise linearity of the Well function. (`calcLpTokenSupply`)

Based on this assumption, the token amount to send to the LP is calculated as `tokenAmountsOut[i] = (lpAmountIn * reserves[i]) / lpTokenSupply`.

But Well creators have freedom of choosing any kind of Well functions and recently non-linear (quadratic) function AMMs are being used by some new protocols. (See Numoen : [https://numoen.gitbook.io/numoen/](https://numoen.gitbook.io/numoen/ "‌"))

For non-linear Well functions, the current calculation of `tokenAmountsOut` will break the Well’s invariant.

**Suggested Mitigation:**

Because the protocol intends to provide freedom of choosing Well function , don’t try to calculate the token out amount. Instead, require the Well’s invariant does not change whenever `reserves` change.

‌

**Reference:**

[https://github.com/code-423n4/2023-01-numoen/blob/2ad9a73d793ea23a25a381faadc86ae0c8cb5913/src/core/Pair.sol#L81](https://github.com/code-423n4/2023-01-numoen/blob/2ad9a73d793ea23a25a381faadc86ae0c8cb5913/src/core/Pair.sol#L81 "smartCard-inline")

[https://3849841188-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FGuKdCWSQNAoGbiGZqOHD%2Fuploads%2FDN7H9CpyFTZ0lBit1Owk%2Fnumoen_whitepaper (2).pdf?alt=media&token=365db895-9368-4559-ad44-a08ffc31f0a2](https://3849841188-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FGuKdCWSQNAoGbiGZqOHD%2Fuploads%2FDN7H9CpyFTZ0lBit1Owk%2Fnumoen_whitepaper%20(2).pdf?alt=media&token=365db895-9368-4559-ad44-a08ffc31f0a2 "‌")

‌


## [L-1] The event `Swap` in transfer should go after the external token call
The event \`Swap\` in transfer should go after the external token call

```
emit Swap(fromToken, toToken, amountIn, amountOut, recipient);
```

Move this line up

