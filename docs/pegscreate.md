## tl;dr ##

Step 1 - Create Tokens
Step 2 - Create an Oracle, register as a publisher and subscribe.
Step 3 - Bind the Tokens and Oracles into a Gateway
Step 4 - Create a Pegs Contract
Step 5 - Stop the Pegs chain, and restart with `earlytxid` launch parameter
Step 6 - Run the Oraclefeed app to maintain the Gateway and monitor deposits / withdrawls.
Step X - Use a different node and pubkey to deposit source coins into the Gateway from the external chain, claim tokens on the Pegs chain, and open a Pegs account _(use the Pegs Usage TUI)._

_[ For full tutorial and Pegs command line RPC methods info, see http://developers.komodo.com/ ]_

PegCC builds upon on the existing Antara modules Tokens, Gateways, Prices and Oracles.
Tokens are created, and transmitted across chains using Gateways for use within the Pegs chain.

First, a Tokens contract is created on the Pegs chain. The token name must be set to the ticker of the source chain (e.g. KMD). These tokens will represent coins from the source chain which are redeemed as a loan, backed by the value of the source coins (tracked via the Prices module) deposited into the Gateway. As the source coin value fluctuates, the Prices module monitors the debt ratio of a user's deposit against the Tokens on loan. 

Next an Oracle is created to monitor the chain state of the source coin, and communicate information about coins deposited via the Gateway. This oracle must also have the name value set to the source coin ticker, and the datatype set to 'Ihh' to store the source chain's block headers.

Next, a Gateways contract is created by binding the Tokens contract with the Oracle transaction ID and one or more pubkeys. These pubkeys allow for protecting withdrawl of coins locked in the Gateway via "M of N" multisig security. The name value of the Gateway must also be set to the source coin ticker, and the total supply balance of all tokens created in the binded Tokens contract. Additionally, the source coin's pubtype, p2shtype and wiftype are required for the Gateway to function as intended.

Finally, a Pegs contract is created for a set amount of funds, linked to one or more gateways. These funds can be accessed as a secured loan via a Gateways deposit from the external chain. Each chain can only have a single Pegs Contract - to ensure this the Pegs creation transaction ID is added as a launch parameter value for the Pegs chain (e.g. -earlytxid=5ccdff0d29f2f47fb1e349c1ff9ae17977a58763abacf693cd27e98b38fad3f3)

_Note: Pubkeys used to create the Gateway, Token, Oracle and Pegs Contract can not be used to perform gateway deposit._ 

Once the above Token, Oracle, Gateway and Pegs Contracts are prepared, an Oraclefeed app is built and started, using the Gateway and Oracle creation transaction IDs as launch parameters. The Oraclefeed app validates deposits from the source chain (e.g. KMD) to the Pegs chain (e.g PEGSTEST). This app must be active on one or more full nodes running both chains, launched with one of the pubkeys used to bind the Gateway. It is important to ensure these pubkeys are registered as an oracle publisher on the Pegs chain, and sufficiently funded via oracle subscription to cover datafees associated with recording source chain block hashes. With multisig gateways - at a minimum - enough fullnodes and pubkeys must be running the Oraclefeed to validate multisig transactions.

## How it works ##

Via the above, 80% of the value of deposited tokens can be exchanged for a “stablecoin” (e.g. USDK) at current Prices market value as reported by the trustless oracle. It is effectively a “deposit and loan” system, where deposited tokens secure the loan.
The USDK tokens can be traded for fiat / other crypto, or redeemed for the originally deposited crypto used to create them.
If the value of the deposited coin rises, additional USDK is created and available to account holder to withdraw, improving their debt ratio. 
If the value of the deposited coin falls, the worst accounts are subject to liquidation. In this event, a third party can gain a 5% return by paying the debt of the account with an excessive debt ratio (e.g. > 90%). The remainder will be applied to the chain as a whole to improve the global debt ratio to prevent underlying assets of the chain falling below the value of total USDK issued.

For example:
Bob uses gatewaysdeposit to convert 100 KMD to KMDT when the market value is $5 per KMD
Bob uses pegsfund to open a new account and then pegsget to convert this KMDT for 375 USDK.
Bob now has 100 KMD (worth $500) securing a “loan” of 375 USDK (worth $375), effectively a 75% debt ratio (375:500). 
Note: This is the opposite of fractional reserve lending!
After some time, KMD rises to $10. Bob’s debt ratio is now a very healthy 37.5% (375:1000). 
Bob decides to take some profit and exchanges for an additional 375 USDK, rising his debt ratio to 75% (750:1000). 
Bob trades 250 USDK over the counter for $250 USD fiat.
At this stage, Bob’s original 100 KMDT deposit worth $500 at time of account creation has been converted into 750 USDK. He has sold part of this for $250 in fiat, still has 100KMD (worth $1000) securing his account, and has 500 USDK (worth $500) to trade with - a combined total value of $1750 from his original input of 100KMD ($500 at time of account creation).

After some more time passes, the price of KMD drops back down to $8.25. Bob’s debt ratio is now at a dangerous level of 90.0909% (750:825), and subject to liquidation.
Alice uses pegsworstaccounts and sees Bob’s debt ratio has left him vulnerable. She decides to liquidate Bob’s account using pegsliquidate,  buying out Bob’s account for 750 USDK. 
At the current market price of $8.25, the 100KMD which was securing Bob’s account is worth $825. Alice receives a 5% bonus worth 37.5 USDK on top of the 750 USDK cost of liquidating Bob’s account, which is paid out in the form of 95.4545 KMDT, worth $787.5 at the current KMD price of $8.25.
The remaining 4.5454 KMDT from Bob’s account is used to maintain the integrity of the pegs chain by reducing the global debt ratio.
Bob still has his remaining 500 USDK (worth $500), and the US$250 fiat he traded for earlier ($750 total). 
The liquidated 100 KMDT account previously securing Bob’s account (worth $825) is closed, netting Bob a loss of $75 against current $8.25 KMD price at liquidation for failing to maintain a good debt ratio. Fortunately for Bob, he’s still up $250 against the original $500 input at account creation (100 KMD at $5), and has suffered no net loss.
As Bob no longer has an account, he can use pegsexchange to convert his USDK to KMDT and either cash out with pegsredeem to reclaim 90 KMD, or use pegsfund to open a new account and then pegsget to convert up to 80% of his KMDT to USDK.