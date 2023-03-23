
| Finding                                                                                                 | Severity | Status   |
| :-------------------------------------------------------------------------------------------------------| :------- | :------- |
| [H-1 ActivePool._rebalance() does not take into account the case when the vault's strategy gets loss](#h-1-activepool_rebalance-does-not-take-into-account-the-case-when-the-vaults-strategy-gets-loss) |H| Open |
| [H-1 Users would lose some shares during withdrawal in `ReaperVaultV2._withdraw()`.](#h-1-users-would-lose-some-shares-during-withdrawal-in-reapervaultv2_withdraw) |H| Open |
| [M-1 "Dust" collaterals/shares are not cleared in ActivePool._rebalance()](#m-1-dust-collateralsshares-are-not-cleared-in-activepool_rebalance) |M| Open |

## [H-1] ActivePool._rebalance() does not take into account the case when the vault's strategy gets loss
ActivePool.\_rebalance() does not consider the case when the vault's strategy gets loss

https://github.com/code-423n4/2023-02-ethos/blob/73687f32b934c9d697b97745356cdf8a1f264955/Ethos-Core/contracts/ActivePool.sol#L251
https://github.com/code-423n4/2023-02-ethos/blob/73687f32b934c9d697b97745356cdf8a1f264955/Ethos-Core/contracts/ActivePool.sol#L282
https://github.com/code-423n4/2023-02-ethos/blob/73687f32b934c9d697b97745356cdf8a1f264955/Ethos-Core/contracts/ActivePool.sol#L288

## Impact

The \_rebalance() reverts if a strategy gets loss.
Because \_rebalance() is called on all important workflows, this leads to insolvency of the protocol.

## Proof of Concept

The protocol uses ReaperVaultERC4626 to manage the collateral assets and farm profit.
The vaults are connected to whitelisted strategies.

But it is not guaranteed that the strategies earn profit all the time.

On the other hand, in several places of ActivePool.\_rebalance(), the protocol assumes that it can get more than deposits all the time.

At L251, where the protocol calculates the profit by subtracting the stored `yieldingAmount` from the `sharesToAssets`, this will revert if the strategy got loss.

```solidity
ActivePool.sol
242:         // how much has been allocated as per our internal records?
243:         vars.currentAllocated = yieldingAmount[_collateral];//@audit-info current yield deposit
244:
245:         // what is the present value of our shares?
246:         vars.yieldGenerator = IERC4626(yieldGenerator[_collateral]);
247:         vars.ownedShares = vars.yieldGenerator.balanceOf(address(this));
248:         vars.sharesToAssets = vars.yieldGenerator.convertToAssets(vars.ownedShares);
249:
250:         // if we have profit that's more than the threshold, record it for withdrawal and redistribution
251:         vars.profit = vars.sharesToAssets.sub(vars.currentAllocated);//@audit-issue profit from the farming, this can revert!
252:         if (vars.profit < yieldClaimThreshold[_collateral]) {
253:             vars.profit = 0;
254:         }
```

At L282 where the protocol withdraws specifying the collateral amount to receive but it will revert if the strategy lost.

```solidity
ActivePool.sol
276:         // + means deposit, - means withdraw
277:         vars.netAssetMovement = int256(vars.toDeposit) - int256(vars.toWithdraw) - int256(vars.profit);
278:         if (vars.netAssetMovement > 0) {
279:             IERC20(_collateral).safeIncreaseAllowance(yieldGenerator[_collateral], uint256(vars.netAssetMovement));
280:             IERC4626(yieldGenerator[_collateral]).deposit(uint256(vars.netAssetMovement), address(this));
281:         } else if (vars.netAssetMovement < 0) {
282:             IERC4626(yieldGenerator[_collateral]).withdraw(uint256(-vars.netAssetMovement), address(this), address(this));//@audit-info coll received, this can revert
283:         }
```

Because \_rebalance() is called on all important workflows, this leads to insolvency of the protocol.

## Tools Used

Manual Review

## Recommended Mitigation Steps

Do not assume `sharesToAssets>yieldingAmount` at all places mentioned and handle appropriately.



## [H-1] Users would lose some shares during withdrawal in `ReaperVaultV2._withdraw()`.
Users would lose some shares during withdrawal in `ReaperVaultV2._withdraw()`.

https://github.com/code-423n4/2023-02-ethos/blob/73687f32b934c9d697b97745356cdf8a1f264955/Ethos-Vault/contracts/ReaperVaultV2.sol#L401

## Impact
`ReaperVaultV2._withdraw()` burns 100% of shares even if the vault balance is less than the required underlying amount.

As a result, users would lose some shares during withdrawal.

## Proof of Concept
Users can receive underlying tokens by burning their shares using `_withdraw()`.

If the vault doesn't have enough underlying balance, it withdraws from strategies inside `withdrawalQueue`.

```solidity
File: ReaperVaultV2.sol
359:     function _withdraw(
360:         uint256 _shares,
361:         address _receiver,
362:         address _owner
363:     ) internal nonReentrant returns (uint256 value) {
364:         require(_shares != 0, "Invalid amount");
365:         value = (_freeFunds() * _shares) / totalSupply();
366:         _burn(_owner, _shares);
367: 
368:         if (value > token.balanceOf(address(this))) { 
398:             ....
399:             vaultBalance = token.balanceOf(address(this));
400:             if (value > vaultBalance) {
401:                 value = vaultBalance; //@audit should reduce shares accordingly
402:             }
403: 
404:             require(
405:                 totalLoss <= ((value + totalLoss) * withdrawMaxLoss) / PERCENT_DIVISOR,
406:                 "Withdraw loss exceeds slippage"
407:             );
408:         }
409: 
410:         token.safeTransfer(_receiver, value);
411:         emit Withdraw(msg.sender, _receiver, _owner, value, _shares);
412:     }
```

After withdrawing from the strategies of `withdrawalQueue`, it applies the max cap at L401.

But as we can see from [setWithdrawalQueue()](https://github.com/code-423n4/2023-02-ethos/blob/73687f32b934c9d697b97745356cdf8a1f264955/Ethos-Vault/contracts/ReaperVaultV2.sol#L258), `withdrawalQueue` wouldn't contain all of the active strategies and the above condition at L400 will be true.

In this case, users will get fewer underlying amounts after burning the whole shares that they requested.

As a reference, it recalculates the shares for the above case in [Yearn vault](https://github.com/yearn/yearn-vaults/blob/master/contracts/Vault.vy#L1151).

```solidity
    if value > vault_balance:
        value = vault_balance
        # NOTE: Burn # of shares that corresponds to what Vault has on-hand,
        #       including the losses that were incurred above during withdrawals
        shares = self._sharesForAmount(value + totalLoss)
```

## Tools Used
Manual Review

## Recommended Mitigation Steps
We should recalculate the shares and burn them rather than burn all shares.


## [M-1] "Dust" collaterals/shares are not cleared in ActivePool._rebalance()
Dust collaterals/shares are not cleared in ActivePool.\_rebalance()

https://github.com/code-423n4/2023-02-ethos/blob/73687f32b934c9d697b97745356cdf8a1f264955/Ethos-Core/contracts/ActivePool.sol#L252
https://github.com/code-423n4/2023-02-ethos/blob/73687f32b934c9d697b97745356cdf8a1f264955/Ethos-Core/contracts/ActivePool.sol#L267

## Impact

The unclaimed “dust” profit will be locked in the vault. Because the affected amount will be not substantial and it will occur only for edge cases, evaluate the severity to Med.

## Proof of Concept

The protocol uses `yieldClaimThreshold` to prevent unnecessary transfer of dust collateral profit (maybe to save gas?).

```solidity
ActivePool.sol
252:         if (vars.profit < yieldClaimThreshold[_collateral]) {
253:             vars.profit = 0;//@audit-issue check how the dust remaining in the vault are processed in the end
254:         }
```

And if `_amountLeavingPool==collAmount[_collateral]`, i.e. for the “last” withdrawal from the vault, the profit under the threshold is not claimed while the protocol considers it does not have any collaterals left in the vault.

As a result, the unclaimed “dust” profit will be locked in the vault. Because the affected amount will be not substantial and it will occur only for edge cases, evaluate the severity to Med.

## Tools Used

Manual Review

## Recommended Mitigation Steps

At L266, check if `vars.finalBalance==0` and add the profit to the target withdraw amount (or redeem the whole owned shares).
The redeemed profit will be distributed by the following logic.


