from brownie import Lottery, config, network
from .helpful_scripts import get_account, get_contract, fund_with_link
from time import sleep


def deploy_lottery() -> Lottery:
    account = get_account()
    network_config = config["networks"][network.show_active()]

    lottery = Lottery.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        network_config["fee"] * 10 ** 18,
        network_config["keyhash"],
        {"from": account},
        publish_source=network_config.get("verify", False),
    )
    print("Deployed lottery!")
    return lottery


def start_lottery():
    account = get_account()
    lottery = Lottery[-1]
    lottery.startLottery({"from": account}).wait(1)
    print("The lottery is started!")


def enter_lottery():
    account = get_account()
    lottery = Lottery[-1]
    value = lottery.getEntranceFee() + 100_000_000
    lottery.enter({"from": account, "value": value}).wait(1)
    print("You entered the lottery!")


def end_lottery():
    account = get_account()
    lottery = Lottery[-1]
    # fund the contract
    # then end the lottery
    tx = fund_with_link(lottery.address)
    tx.wait(1)
    ending_transaction = lottery.endLottery({"from": account})
    ending_transaction.wait(1)
    sleep(60)
    print(f"{lottery.recentWinner()} is the new winner!")


def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()
