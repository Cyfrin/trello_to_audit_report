---
title: "Cyfrin LiquidSDIndexPool Mitigation Audit Report"
author: Cyfrin.io
header-includes:
  - \usepackage{titling}
  - \usepackage{graphicx}
linkcolor: blue
urlcolor: blue
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

