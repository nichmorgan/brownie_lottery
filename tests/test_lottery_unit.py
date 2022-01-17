from brownie import network, exceptions
from scripts.deploy_lottery import deploy_lottery
from web3 import Web3
import pytest

from scripts.helpful_scripts import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    fund_with_link,
    get_account,
    get_contract,
)


def test_get_entrance_fee():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()

    # 2,000 eth / usd
    # usdEntryFee is 50
    # 2000/1 == 50/x == 0.025
    expected_entrace_fee = Web3.toWei(0.025, "ether")
    entrance_fee = lottery.getEntranceFee()
    assert expected_entrace_fee == entrance_fee


def test_cant_enter_unless_starter():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({"from": get_account(), "value": lottery.getEntranceFee})


def test_can_start_and_enter_lottery():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    assert lottery.players(0) == account


def test_can_end_lottery():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    lottery.endLottery({"from": account})
    assert lottery.lottery_state() == 2


def test_can_pick_winner_corretly():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})

    players_count = 3
    for index in range(players_count):
        lottery.enter(
            {"from": get_account(index=index), "value": lottery.getEntranceFee()}
        )

    fund_with_link(lottery)
    transaction = lottery.endLottery({"from": account})
    requestId = transaction.events["RequestedRandomness"]["requestId"]

    STATIC_RNG = 777
    get_contract("vrf_coordinator").callBackWithRandomness(
        requestId, STATIC_RNG, lottery.address, {"from": account}
    )
    starting_balance_of_account = account.balance()
    balance_of_lottery = lottery.balance()
    assert lottery.recentWinner() == get_account(index=STATIC_RNG % players_count)
    assert lottery.balance() == 0
    assert account.balance() == starting_balance_of_account + balance_of_lottery
