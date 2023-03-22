
| Finding                                                                             | Severity | Status   |
| :-----------------------------------------------------------------------------------| :------- | :------- |
| [H-1 ActivePool._rebalance() does not take into account the case when the vault's strategy gets loss](#h-1-activepool_rebalance-does-not-take-into-account-the-case-when-the-vaults-strategy-gets-loss) |H| Open |
| [H-2 Users would lose some shares during withdrawal in `ReaperVaultV2._withdraw()`.](#h-2-users-would-lose-some-shares-during-withdrawal-in-reapervaultv2_withdraw) |H| Open |
| [M-1 "Dust" collaterals/shares are not cleared in ActivePool._rebalance()](#m-1-dust-collateralsshares-are-not-cleared-in-activepool_rebalance) |M| Open |
| [M-2 Some tokens do not allow changing allowance from non-zero to non-zero](#m-2-some-tokens-do-not-allow-changing-allowance-from-non-zero-to-non-zero) |M| Open |
| [M-3 Lack of blacklisting collateral](#m-3-lack-of-blacklisting-collateral) |M| Open |
| [M-4 strategy.activation is not reset on revoking and this prevents adding it back](#m-4-strategyactivation-is-not-reset-on-revoking-and-this-prevents-adding-it-back) |M| Open |
| [M-5 In `ReaperVaultV2`, we should update `lockedProfit` and `lastReport` before changing `lockedProfitDegradation`.](#m-5-in-reapervaultv2-we-should-update-lockedprofit-and-lastreport-before-changing-lockedprofitdegradation) |M| Open |
| [M-6 `ReaperBaseStrategyv4.harvest()` might revert in an emergency.](#m-6-reaperbasestrategyv4harvest-might-revert-in-an-emergency) |M| Open |
| [M-7 There should be an option to rescue the underlying token in `ReaperVaultV2.sol`](#m-7-there-should-be-an-option-to-rescue-the-underlying-token-in-reapervaultv2sol) |M| Open |
| [M-8 `ReaperVaultV2._withdraw()` will revert if one strategy in `withdrawalQueue` is in the debt.](#m-8-reapervaultv2_withdraw-will-revert-if-one-strategy-in-withdrawalqueue-is-in-the-debt) |M| Open |
| [M-9 The vault might charge more underlying tokens from strategies because `ReaperVaultV2.report()` uses `repayment` wrongly.](#m-9-the-vault-might-charge-more-underlying-tokens-from-strategies-because-reapervaultv2report-uses-repayment-wrongly) |M| Open |
| [Q-1 QA Findings](#q-1-qa-findings) |Q| Open |

## [H-1] ActivePool._rebalance() does not take into account the case when the vault's strategy gets loss
[Ethos-Core/contracts/ActivePool.sol#L251](https://github.com/ChainAccelOrg/2023-02-ethos/blob/98f7ccc3d7e84a825cca4f5abb04e2ef35562ce5/Ethos-Core/contracts/ActivePool.sol#L251 "‌")

[Ethos-Core/contracts/ActivePool.sol#L282](https://github.com/ChainAccelOrg/2023-02-ethos/blob/98f7ccc3d7e84a825cca4f5abb04e2ef35562ce5/Ethos-Core/contracts/ActivePool.sol#L282 "‌")

[Ethos-Core/contracts/ActivePool.sol#L288](https://github.com/ChainAccelOrg/2023-02-ethos/blob/98f7ccc3d7e84a825cca4f5abb04e2ef35562ce5/Ethos-Core/contracts/ActivePool.sol#L288 "‌")

### Summary

The protocol uses `ReaperVaultERC4626` to manage the collateral assets and farm profit. The vaults are connected to whitelisted strategies.

But it is not guaranteed that the strategies earn profit all the time.

On the other hand, in several places of `ActivePool._rebalance()`, the protocol assumes that it can get more than deposits all the time.

For example, the protocol stores the deposit to the vault as `yieldingAmount` and use that to calculate the profit saying `more precisely`. But if the strategy incurs loss, the actual profit will be less than the calculated amount and it leads to the loss of pool.

Another example is at L282 where the protocol withdraws specifying the collateral amount to receive but it will revert at the end if the strategy lost.

Another example is at L251, where the protocol calculates the profit by subtracting the stored `yieldingAmount` from the `sharesToAssets`. This will revert as well if the strategy lost.

### Impact

The `_rebalance()` will revert almost all the time due to the third example. Because `_rebalance()` is called on important occasions, this leads to **insolvency of the protocol**.

### Mitigation

Do not assume `sharesToAssets>yieldingAmount` at all places mentioned and handle appropriately.

$a/b$


## [H-2] Users would lose some shares during withdrawal in `ReaperVaultV2._withdraw()`.
[Ethos-Vault/contracts/ReaperVaultV2.sol#L401](https://github.com/code-423n4/2023-02-ethos/blob/73687f32b934c9d697b97745356cdf8a1f264955/Ethos-Vault/contracts/ReaperVaultV2.sol#L401 "‌")

`https://github.com/yearn/yearn-vaults/blob/master/contracts/Vault.vy#L1151`

## Summary

In `ReaperVaultV2._withdraw()` it shouldn’t burn 100% of shares if vault balance is less than `value`.

It should recalculate the share like the yearn vault.

```
        if value > vault_balance:
            value = vault_balance
            # NOTE: Burn # of shares that corresponds to what Vault has on-hand,
            #       including the losses that were incurred above during withdrawals
            shares = self._sharesForAmount(value + totalLoss)
```

‌

## Impact

`ReaperVaultV2._withdraw()` burns 100% of shares even if the vault balance is less than the required underlying amount.

As a result, users would lose some shares during withdrawal.

## Mitigation

It should reduce shares to burn according to the final amount.


## [M-1] "Dust" collaterals/shares are not cleared in ActivePool._rebalance()
[Ethos-Core/contracts/ActivePool.sol#L252](https://github.com/ChainAccelOrg/2023-02-ethos/blob/98f7ccc3d7e84a825cca4f5abb04e2ef35562ce5/Ethos-Core/contracts/ActivePool.sol#L252 "‌")

[Ethos-Core/contracts/ActivePool.sol#L267](https://github.com/ChainAccelOrg/2023-02-ethos/blob/98f7ccc3d7e84a825cca4f5abb04e2ef35562ce5/Ethos-Core/contracts/ActivePool.sol#L267 "‌")

### Summary

The protocol uses `yieldClaimThreshold` to prevent unnecessary transfer of dust collateral profit (maybe to save gas?). And if `_amountLeavingPool==collAmount[_collateral]`, i.e. for the “last” withdrawal from the vault, the profit under the threshold is not claimed while the protocol considers it does not have any collaterals left in the vault.

### Impact

The unclaimed “dust” profit will be locked in the vault. Because the affected amount will be not substantial and it will occur only for edge cases, evaluate the severity to Med.

### Mitigation

At L266, check if `vars.finalBalance==0` and add the profit to the target withdraw amount (or redeem the whole owned shares). The redeemed profit will can be distributed by the following lines.


## [M-2] Some tokens do not allow changing allowance from non-zero to non-zero
### Code

[SafeERC20.sol#L48](https://github.com/ChainAccelOrg/2023-02-ethos/blob/49b81ba98f3e121bc0bd2f14b97e433ef52e9468/Ethos-Core/contracts/Dependencies/SafeERC20.sol#L48 "‌")

[ActivePool.sol#L180](https://github.com/ChainAccelOrg/2023-02-ethos/blob/98f7ccc3d7e84a825cca4f5abb04e2ef35562ce5/Ethos-Core/contracts/ActivePool.sol#L180 "‌")

### Summary

Some tokens (like USDT) do not work when changing the allowance from an existing non-zero allowance value. They must first be approved by zero and then the actual allowance must be approved.

### Ref

[https://github.com/code-423n4/2022-12-tigris-findings/issues/104](https://github.com/code-423n4/2022-12-tigris-findings/issues/104 "smartCard-inline")

[https://github.com/d-xo/weird-erc20#approval-race-protections](https://github.com/d-xo/weird-erc20#approval-race-protections "smartCard-inline")


## [M-3] Lack of blacklisting collateral
[Ethos-Core/contracts/CollateralConfig.sol#L128](https://github.com/ChainAccelOrg/2023-02-ethos/blob/98f7ccc3d7e84a825cca4f5abb04e2ef35562ce5/Ethos-Core/contracts/CollateralConfig.sol#L128 "‌")

[Ethos-Core/contracts/CollateralConfig.sol#L106](https://github.com/ChainAccelOrg/2023-02-ethos/blob/98f7ccc3d7e84a825cca4f5abb04e2ef35562ce5/Ethos-Core/contracts/CollateralConfig.sol#L106 "‌")

### Summary

The protocol is designed to be able to support multiple ERC20 tokens.

All the important interactions are checked to be for _allowed_ collateral tokens.

The _allowed_ collaterals are set on the initialization of `CollateralConfig`.

But there is no way to `remove` or `blacklist` an existing collateral token.

While I guess the protocol team is aware of this, I believe it’s worth flagging it again because this is very dangerous. Imagine an allowed collateral is exploited in some way. It might lead to massive liquidation of troves and StabilityPool depositors will end up losing LUSD and getting that token (very likely to have no value anymore).

It is interesting that the protocol team still reserved a function `updateCollateralRatios` that allows lowering CR.

### Impact

It is impossible to protect the protocol (SP depositors) from an external incidents. Evaluate the severity to Med because it assumes some external exploits.

### Mitigation

Add a new admin function to blacklist a specific collateral.


## [M-4] strategy.activation is not reset on revoking and this prevents adding it back
[Ethos-Vault/contracts/ReaperVaultV2.sol#L205](https://github.com/ChainAccelOrg/2023-02-ethos/blob/1849f544e3fa05314da08a17e4d0dbaa2e3df913/Ethos-Vault/contracts/ReaperVaultV2.sol#L205 "‌")

[Ethos-Vault/contracts/ReaperVaultV2.sol#L152](https://github.com/ChainAccelOrg/2023-02-ethos/blob/1849f544e3fa05314da08a17e4d0dbaa2e3df913/Ethos-Vault/contracts/ReaperVaultV2.sol#L152 "‌")

[Ethos-Vault/contracts/ReaperVaultV2.sol#L493](https://github.com/ChainAccelOrg/2023-02-ethos/blob/1849f544e3fa05314da08a17e4d0dbaa2e3df913/Ethos-Vault/contracts/ReaperVaultV2.sol#L493 "‌")

### Summary

In `ReaperVaultV2.sol`, strategies are managed by a mapping `strategies`.

Each strategy is stored as `StrategyParams` and `activation` field is used to store the activation block timestamp.

Looking at the usage, this field is also used to see if a strategy is an enabled one.

But in the function `revokeStrategy()` this field is not removed.

This affects a few places:

- It is possible to re-add a removed strategy back because this field is required to be empty at L151
- Removed strategies can still call the function `report()`.

### Impact

For now setting the severity to Med but need a double look to see if this can cause loss to the protocol in some way, especially via `report()`

### Mitigation

Add `strategies[_strategy].activated = 0;` in the function `revokeStrategy()`.


## [M-5] In `ReaperVaultV2`, we should update `lockedProfit` and `lastReport` before changing `lockedProfitDegradation`.
Ethos-Vault/contracts/ReaperVaultV2.sol#L620

Ethos-Vault/contracts/ReaperVaultV2.sol#L419

## Summary

`lockedProfitDegradation`` is used to calculate the locked profit for vault’s balance.

But it doesn’t update `lastReport` before changing `lockedProfitDegradation`` so already unlocked profit might be locked again with the new setting.

## Impact

The logic of locked profit calculation wouldn’t work as expected as the degradation ratio for past can be changed.

## Mitigation

`lockedProfit` and `lastReport` should be updated before changing the ratio.


## [M-6] `ReaperBaseStrategyv4.harvest()` might revert in an emergency.
[https://github.com/code-423n4/2023-02-ethos/blob/73687f32b934c9d697b97745356cdf8a1f264955/Ethos-Vault/contracts/abstract/ReaperBaseStrategyv4.sol#L109](https://github.com/code-423n4/2023-02-ethos/blob/73687f32b934c9d697b97745356cdf8a1f264955/Ethos-Vault/contracts/abstract/ReaperBaseStrategyv4.sol#L109 "smartCard-inline")

[https://github.com/code-423n4/2023-02-ethos/blob/73687f32b934c9d697b97745356cdf8a1f264955/Ethos-Vault/contracts/ReaperStrategyGranarySupplyOnly.sol#L200](https://github.com/code-423n4/2023-02-ethos/blob/73687f32b934c9d697b97745356cdf8a1f264955/Ethos-Vault/contracts/ReaperStrategyGranarySupplyOnly.sol#L200 "smartCard-inline")


## [M-7] There should be an option to rescue the underlying token in `ReaperVaultV2.sol`



## [M-8] `ReaperVaultV2._withdraw()` will revert if one strategy in `withdrawalQueue` is in the debt.



## [M-9] The vault might charge more underlying tokens from strategies because `ReaperVaultV2.report()` uses `repayment` wrongly.



## [Q-1] QA Findings
### Core contracts are susceptible to initializer re-entrancy due to OpenZeppelin version advisory

The version of OpenZeppelin in the core package falls within this advisory, so advised to upgrade to avoid accidentally adding a vulnerability if external calls are made [https://github.com/OpenZeppelin/openzeppelin-contracts/security/advisories/GHSA-9c22-pwxw-p6hx](https://github.com/OpenZeppelin/openzeppelin-contracts/security/advisories/GHSA-9c22-pwxw-p6hx "smartCard-inline")

### Use emit keyword for events

[https://github.com/code-423n4/2023-02-ethos/blob/main/Ethos-Core/contracts/ActivePool.sol#L194](https://github.com/code-423n4/2023-02-ethos/blob/73687f32b934c9d697b97745356cdf8a1f264955/Ethos-Core/contracts/ActivePool.sol#L194 "‌"); [https://github.com/code-423n4/2023-02-ethos/blob/main/Ethos-Core/contracts/ActivePool.sol#L201](https://github.com/code-423n4/2023-02-ethos/blob/73687f32b934c9d697b97745356cdf8a1f264955/Ethos-Core/contracts/ActivePool.sol#L201 "‌"); [https://github.com/code-423n4/2023-02-ethos/blob/main/Ethos-Core/contracts/SortedTroves.sol#L198](https://github.com/code-423n4/2023-02-ethos/blob/73687f32b934c9d697b97745356cdf8a1f264955/Ethos-Core/contracts/SortedTroves.sol#L198 "‌")

### RedemptionHelper not included in function name/revert string

[https://github.com/code-423n4/2023-02-ethos/blob/main/Ethos-Core/contracts/ActivePool.sol#L327-L335](https://github.com/code-423n4/2023-02-ethos/blob/73687f32b934c9d697b97745356cdf8a1f264955/Ethos-Core/contracts/ActivePool.sol#L327-L335 "‌")

### Inconsistent use of uint/uint256

Can cause issues when encoding (but all fine currently it seems)

### Could precompute addresses beforehand instead of setAddresses functions

[https://github.com/transmissions11/solmate/issues/207](https://github.com/transmissions11/solmate/issues/207 "‌")

### Re-entrancy risk in openTrove

Although unlikely bad collateral will be included [https://github.com/code-423n4/2023-02-ethos/blob/main/Ethos-Core/contracts/BorrowerOperations.sol#L231](https://github.com/code-423n4/2023-02-ethos/blob/73687f32b934c9d697b97745356cdf8a1f264955/Ethos-Core/contracts/BorrowerOperations.sol#L231 "‌")

### Use enum for comparisons without casting to uint

[https://github.com/code-423n4/2023-02-ethos/blob/main/Ethos-Core/contracts/BorrowerOperations.sol#L543](https://github.com/code-423n4/2023-02-ethos/blob/73687f32b934c9d697b97745356cdf8a1f264955/Ethos-Core/contracts/BorrowerOperations.sol#L543 "‌")

### Inconsistent use of `_100pct` / `DECIMAL_PRECISION`

[https://github.com/code-423n4/2023-02-ethos/blob/main/Ethos-Core/contracts/BorrowerOperations.sol#L650](https://github.com/code-423n4/2023-02-ethos/blob/73687f32b934c9d697b97745356cdf8a1f264955/Ethos-Core/contracts/BorrowerOperations.sol#L650 "‌"); [https://github.com/code-423n4/2023-02-ethos/blob/main/Ethos-Core/contracts/TroveManager.sol#L1412](https://github.com/code-423n4/2023-02-ethos/blob/73687f32b934c9d697b97745356cdf8a1f264955/Ethos-Core/contracts/TroveManager.sol#L1412 "‌")

### Typehashes correct but use keccak256 to avoid making mistakes

(evaluated at compile time anyway) [https://github.com/code-423n4/2023-02-ethos/blob/main/Ethos-Core/contracts/LUSDToken.sol#L41-L44](https://github.com/code-423n4/2023-02-ethos/blob/73687f32b934c9d697b97745356cdf8a1f264955/Ethos-Core/contracts/LUSDToken.sol#L41-L44 "‌")

### `withdrawFromSp` doesn't `_requireNonZeroAmount()` unlike `provideToSP`

… but gains are paid out and snapshots updated without sending LUSD. Perhaps should be consistent between functions though.

### Remove console.log imports

All instances should be removed

### Is lack of initializer access control intentional?

[https://github.com/code-423n4/2023-02-ethos/blob/main/Ethos-Vault/contracts/ReaperStrategyGranarySupplyOnly.sol#L62-L67](https://github.com/code-423n4/2023-02-ethos/blob/73687f32b934c9d697b97745356cdf8a1f264955/Ethos-Vault/contracts/ReaperStrategyGranarySupplyOnly.sol#L62-L67 "‌")

### No rewards swapped in `_harvestCore`

When \`steps\` are not initialized it seems admin has to \`setHarvestSteps\` first, but this may not happen so rewards aren't swapped. [https://github.com/code-423n4/2023-02-ethos/blob/main/Ethos-Vault/contracts/ReaperStrategyGranarySupplyOnly.sol#L114-L125](https://github.com/code-423n4/2023-02-ethos/blob/73687f32b934c9d697b97745356cdf8a1f264955/Ethos-Vault/contracts/ReaperStrategyGranarySupplyOnly.sol#L114-L125 "‌")

### Use `_disableInitializers()`

[https://github.com/code-423n4/2023-02-ethos/blob/main/Ethos-Vault/contracts/abstract/ReaperBaseStrategyv4.sol#L61](https://github.com/code-423n4/2023-02-ethos/blob/73687f32b934c9d697b97745356cdf8a1f264955/Ethos-Vault/contracts/abstract/ReaperBaseStrategyv4.sol#L61 "‌")

### Remove deployer default admin role

Default admin is reserved for most privileged role which should be multisig [https://github.com/code-423n4/2023-02-ethos/blob/main/Ethos-Vault/contracts/ReaperVaultV2.sol#L132](https://github.com/code-423n4/2023-02-ethos/blob/73687f32b934c9d697b97745356cdf8a1f264955/Ethos-Vault/contracts/ReaperVaultV2.sol#L132 "‌")

### 20BPS erronously set to 20%

[https://github.com/code-423n4/2023-02-ethos/blob/main/Ethos-Vault/contracts/ReaperVaultV2.sol#L155](https://github.com/code-423n4/2023-02-ethos/blob/73687f32b934c9d697b97745356cdf8a1f264955/Ethos-Vault/contracts/ReaperVaultV2.sol#L155 "‌"); [https://github.com/code-423n4/2023-02-ethos/blob/main/Ethos-Vault/contracts/ReaperVaultV2.sol#L181](https://github.com/code-423n4/2023-02-ethos/blob/73687f32b934c9d697b97745356cdf8a1f264955/Ethos-Vault/contracts/ReaperVaultV2.sol#L155 "‌")

### Follow CEI

CEI violation. Re-entrancy which could affect locked profit calculations below or chain with burning shares before charging fees in `_withdraw`. Although would require a malicious strategy which massively lowers likelihood and hence severity. [https://github.com/code-423n4/2023-02-ethos/blob/73687f32b934c9d697b97745356cdf8a1f264955/Ethos-Vault/contracts/ReaperVaultV2.sol#L528](https://github.com/code-423n4/2023-02-ethos/blob/73687f32b934c9d697b97745356cdf8a1f264955/Ethos-Vault/contracts/ReaperVaultV2.sol#L528 "smartCard-inline")

### Gas

could save a call by using \`type(uint256).max\` here as function performs min againt withdrawable amount anyway [https://github.com/code-423n4/2023-02-ethos/blob/main/Ethos-Vault/contracts/ReaperStrategyGranarySupplyOnly.sol#L105](https://github.com/code-423n4/2023-02-ethos/blob/73687f32b934c9d697b97745356cdf8a1f264955/Ethos-Vault/contracts/ReaperStrategyGranarySupplyOnly.sol#L105 "‌")

