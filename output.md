---
title: "Cyfrin LiquidSDIndexPool Mitigation Audit Report"
author: Cyfrin.io
date: March 7, 2023
header-includes:
  - \usepackage{titling}
  - \usepackage{graphicx}
---

\begin{titlepage}
    \centering
    \begin{figure}[h]
        \centering
        \includegraphics[width=0.5\textwidth]{./examples/cyfrin-logo.pdf} 
    \end{figure}
    \vspace*{2cm}
    {\Huge\bfseries LinkPool LiquidSDIndexPool Audit Report\par}
    \vspace{1cm}
    {\Large Version 2.0\par}
    \vspace{2cm}
    {\Large\itshape Cyfrin.io\par}
    \vfill
    {\large \today\par}
\end{titlepage}

\maketitle

# LinkPool LiquidSDIndexPool Audit Report

Version 1.0

Prepared by: [Cyfrin](https://cyfrin.io)
Lead Auditors: 

- [Patrick Collins](https://twitter.com/PatrickAlphaC)

- [Ben Sacchetti](https://twitter.com/dark_bends)
 
Assisting Auditors:

- [Giovanni Di Siena](https://twitter.com/giovannidisiena)

- [Hans](https://twitter.com/hansfriese)

## Disclaimer 

The Cyfrin team makes all effort to find as many vulnerabilities in the code in the given time period, but holds no responsibilities for the the findings provided in this document. A security audit by the team is not an endorsement of the underlying business or product. The audit was time-boxed to two weeks, and the review of the code is solely on the security aspects of the solidity implementation of the contracts. 


# Protocol Summary

The LinkPool LiquidSDIndexPool protocol allows users to deposit liquid staking derivative tokens (LSDs) like Rocket Pool ETH (rETH) & Lido ETH (stETH) and, by doing so, receive a token that represents holding a basket of these assets in return. The protocol makes a fee on withdrawls.

This product intends to provide exposure to ETH Staking by averaging rate of the interest across multiple staked ETH derivative protocols. 

# Audit Details 

## Scope Of Audit

Between Februrary 6th 2023 - Feb 17th 2023, the Cyfrin team conducted an audit on the `liquidSDIndex` folder of their [staking-contracts-v2](https://github.com/linkpoolio/staking-contracts-v2) repository. The scope of the audit was as follows:

1. Full audit of the single folder of contracts in the git repository specified by linkpool
   1.  Commit hash: [7084a32](https://github.com/linkpoolio/staking-contracts-v2/tree/7084a329a6a42791941bfad74d1550d1832defb1) of [staking-contracts-v2](https://github.com/linkpoolio/staking-contracts-v2)
   2.  Contracts in the `liquidSDIndex` folder: `staking-contracts-v2/contracts/liquidSDIndex/`
2. Out of scope
   1. The test folder & test contracts in `liquidSDIndex` folder

## Severity Criteria

- High: Assets can be stolen/lost/compromised directly (or indirectly if there is a valid attack path that does not have hand-wavy hypotheticals).
- Medium: Assets not at direct risk, but the function of the protocol or its availability could be impacted, or leak value with a hypothetical attack path with stated assumptions, but external requirements.
- Low: Low impact and low/medium likelihood events where assets are not at risk (or a trivia amount of assets are), state handling might be off, functions are incorrect as to natspec, issues with comments, etc. 
- Informational / Non-Critial: A non-security issue, like a suggested code improvement, a comment, a renamed variable, etc. Auditors did not attempt to find an exhaustive list of these.  
- Gas: Gas saving / performance suggestions. Auditors did not attempt to find an exhaustive list of these.  

## Tools used

- [Slither](https://github.com/crytic/slither)
- [4naly3er](https://github.com/Picodes/4naly3er)
- [foundry](https://book.getfoundry.sh/)
- [Hardhat](https://hardhat.org/)
- [Solodit](https://solodit.xyz/)

## Summary Of Findings

We highly recommend writing fuzz & invariant tests to catch these issues moving forward. 

High   - 2

Medium - 5

Low    - 10


*Key: Ack == Acknowledged*


| Finding                                                                                                 | Severity | Status   |
| :-------------------------------------------------------------------------------------------------------| :------- | :------- |
| [H-1 ActivePool._rebalance() does not take into account the case when the vault's strategy gets loss](#h-1-activepool_rebalance-does-not-take-into-account-the-case-when-the-vaults-strategy-gets-loss) |H| Open |
| [H-1 Users would lose some shares during withdrawal in `ReaperVaultV2._withdraw()`.](#h-1-users-would-lose-some-shares-during-withdrawal-in-reapervaultv2_withdraw) |H| Open |
| [M-1 "Dust" collaterals/shares are not cleared in ActivePool._rebalance()](#m-1-dust-collateralsshares-are-not-cleared-in-activepool_rebalance) |M| Open |
| [M-1 Some tokens do not allow changing allowance from non-zero to non-zero](#m-1-some-tokens-do-not-allow-changing-allowance-from-non-zero-to-non-zero) |M| Open |
| [M-1 Lack of blacklisting collateral](#m-1-lack-of-blacklisting-collateral) |M| Open |
| [M-1 strategy.activation is not reset on revoking and this prevents adding it back](#m-1-strategyactivation-is-not-reset-on-revoking-and-this-prevents-adding-it-back) |M| Open |
| [M-1 In `ReaperVaultV2`, we should update `lockedProfit` and `lastReport` before changing `lockedProfitDegradation`.](#m-1-in-reapervaultv2-we-should-update-lockedprofit-and-lastreport-before-changing-lockedprofitdegradation) |M| Open |
| [M-1 `ReaperBaseStrategyv4.harvest()` might revert in an emergency.](#m-1-reaperbasestrategyv4harvest-might-revert-in-an-emergency) |M| Open |
| [M-1 There should be an option to rescue the underlying token in `ReaperVaultV2.sol`](#m-1-there-should-be-an-option-to-rescue-the-underlying-token-in-reapervaultv2sol) |M| Open |
| [M-1 `ReaperVaultV2._withdraw()` will revert if one strategy in `withdrawalQueue` is in the debt.](#m-1-reapervaultv2_withdraw-will-revert-if-one-strategy-in-withdrawalqueue-is-in-the-debt) |M| Open |
| [M-1 The vault might charge more underlying tokens from strategies because `ReaperVaultV2.report()` uses `repayment` wrongly.](#m-1-the-vault-might-charge-more-underlying-tokens-from-strategies-because-reapervaultv2report-uses-repayment-wrongly) |M| Open |
| [Q-1 QA Findings](#q-1-qa-findings) |Q| Open |

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
Error getting attachment.
Please name the attachment to report.md. The erroring Card ID:
	641af04d96b74c82177e1ed3
URL:
	https://trello.com/c/I5aIjN3X/15-users-would-lose-some-shares-during-withdrawal-in-reapervaultv2withdraw.


## [M-1] "Dust" collaterals/shares are not cleared in ActivePool._rebalance()
Error getting attachment.
Please name the attachment to report.md. The erroring Card ID:
	641af04d96b74c82177e1ec9
URL:
	https://trello.com/c/49MGZSDk/10-dust-collaterals-shares-are-not-cleared-in-activepoolrebalance.


## [M-1] Some tokens do not allow changing allowance from non-zero to non-zero
Error getting attachment.
Please name the attachment to report.md. The erroring Card ID:
	641af04d96b74c82177e1ebf
URL:
	https://trello.com/c/OOuF4eQO/5-some-tokens-do-not-allow-changing-allowance-from-non-zero-to-non-zero.


## [M-1] Lack of blacklisting collateral
Error getting attachment.
Please name the attachment to report.md. The erroring Card ID:
	641af04d96b74c82177e1ecb
URL:
	https://trello.com/c/SprHnrjn/11-lack-of-blacklisting-collateral.


## [M-1] strategy.activation is not reset on revoking and this prevents adding it back
Error getting attachment.
Please name the attachment to report.md. The erroring Card ID:
	641af04d96b74c82177e1ecd
URL:
	https://trello.com/c/2Gq8Otda/12-strategyactivation-is-not-reset-on-revoking-and-this-prevents-adding-it-back.


## [M-1] In `ReaperVaultV2`, we should update `lockedProfit` and `lastReport` before changing `lockedProfitDegradation`.
Error getting attachment.
Please name the attachment to report.md. The erroring Card ID:
	641af04d96b74c82177e1ed5
URL:
	https://trello.com/c/Gp7G4gfF/16-in-reapervaultv2-we-should-update-lockedprofit-and-lastreport-before-changing-lockedprofitdegradation.


## [M-1] `ReaperBaseStrategyv4.harvest()` might revert in an emergency.
Error getting attachment.
Please name the attachment to report.md. The erroring Card ID:
	641af04d96b74c82177e1edb
URL:
	https://trello.com/c/vxP44r6v/19-reaperbasestrategyv4harvest-might-revert-in-an-emergency.


## [M-1] There should be an option to rescue the underlying token in `ReaperVaultV2.sol`
Error getting attachment.
Please name the attachment to report.md. The erroring Card ID:
	641af04d96b74c82177e1edd
URL:
	https://trello.com/c/RL01tBvB/20-there-should-be-an-option-to-rescue-the-underlying-token-in-reapervaultv2sol.


## [M-1] `ReaperVaultV2._withdraw()` will revert if one strategy in `withdrawalQueue` is in the debt.
Error getting attachment.
Please name the attachment to report.md. The erroring Card ID:
	641af04d96b74c82177e1edf
URL:
	https://trello.com/c/1KJkGGEC/21-reapervaultv2withdraw-will-revert-if-one-strategy-in-withdrawalqueue-is-in-the-debt.


## [M-1] The vault might charge more underlying tokens from strategies because `ReaperVaultV2.report()` uses `repayment` wrongly.
Error getting attachment.
Please name the attachment to report.md. The erroring Card ID:
	641af04d96b74c82177e1ee1
URL:
	https://trello.com/c/hCk2C0CT/22-the-vault-might-charge-more-underlying-tokens-from-strategies-because-reapervaultv2report-uses-repayment-wrongly.


## [Q-1] QA Findings
Error getting attachment.
Please name the attachment to report.md. The erroring Card ID:
	641af04d96b74c82177e1ecf
URL:
	https://trello.com/c/N0Hux3bD/13-qa-findings.

