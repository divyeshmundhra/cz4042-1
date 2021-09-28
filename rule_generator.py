import time
import fim
from models import Consequent, Item, Antecedent, ClassAssocationRule
import logging


def convertToCARs(rules):  # coverts apriori rules to CARS format
    """Function for converting apriori rules to CARs format

    rules : Association rules from generateARs
    
    Returns
    -------
    list of CARs

    """
    CARs = []

    for rule in rules:
        rhs_tmp, lhs_tmp, support, confidence = rule
        rhs = Consequent(*rhs_tmp.split(":=:"))  # ['class', 'Iris-setosa']

        # so that the order of items in antecedent is always the same
        lhs_tmp = sorted(list(lhs_tmp))
        lhs_items = [Item(*i.split(":=:")) for i in lhs_tmp]
        lhs = Antecedent(lhs_items)  # convert the antecedents to dict form

        CAR = ClassAssocationRule(
            lhs, rhs, support=support, confidence=confidence
        )  # convert to CAR
        CARs.append(CAR)

    CARs.sort(reverse=True)

    return CARs


def generateARs(
    transactionDB, support=1, confidence=50, maxlen=10, **kwargs
):  # generates Assoc. rules using apriori and converts them to CARS
    """Function for generating ClassAssociationRules from a TransactionDB

    Parameters
    ----------
    transactionDB : TransactionDB

    support : float
    confidence : float
    maxlen : int
    **kwargs : 
        arbitrary number of arguments that will be 
        provided to the fim.apriori function

    Returns
    -------
    list of CARs

    """
    appear = transactionDB.appeardict
    print("Mining top association rules")
    rules = fim.apriori(
        transactionDB.string_representation,
        supp=support,
        conf=confidence,
        mode="o",
        target="r",
        report="sc",
        appear=appear,
        **kwargs,
        zmax=maxlen,
    )

    print("no of association rules from apriori: ", len(rules))
    print("ex rule: ", rules[0])

    return rules


def top_rules(
    transactions,
    appearance={},
    target_rule_count=1000,
    init_support=0.1,
    init_conf=0.5,
    conf_step=0.05,
    supp_step=0.05,
    minlen=2,
    init_maxlen=3,
    total_timeout=100.0,
    max_iterations=30,
):
    """Function for finding the best n (target_rule_count)
    rules from transaction list

    Parameters
    ----------
    transactions : 2D array of strings
        e.g. [["a:=:1", "b:=:3"], ["a:=:4", "b:=:2"]]

    appearance : dictionary
        dictionary specifying rule appearance

    targent_rule_count : int
        target number of rules to mine

    init_conf : float
        confidence from which to start mining

    conf_step : float

    supp_step : float

    minen : int
        minimum len of rules to mine

    init_maxlen : int
        maxlen from which to start mining

    total_timeout : float
        maximum execution time of the function

    max_iterations : int
        maximum iterations to try before stopping
        execution


    Returns
    -------
    list of mined rules. The rules are not ordered.

    """

    starttime = time.time()

    MAX_RULE_LEN = len(transactions[0])

    support = init_support
    conf = init_conf

    maxlen = init_maxlen

    flag = True
    lastrulecount = -1
    maxlendecreased_due_timeout = False
    iterations = 0

    rules = None

    while flag:
        iterations += 1

        if iterations == max_iterations:
            logging.debug("Max iterations reached")
            break

        logging.debug(
            "Running apriori with setting: confidence={}, support={}, minlen={}, maxlen={}, MAX_RULE_LEN={}".format(
                conf, support, minlen, maxlen, MAX_RULE_LEN
            )
        )

        rules_current = fim.arules(
            transactions,
            supp=support,
            conf=conf,
            mode="o",
            report="sc",
            appear=appearance,
            zmax=maxlen,
            zmin=minlen,
        )

        rules = rules_current

        rule_count = len(rules)

        logging.debug("Rule count: {}, Iteration: {}".format(rule_count, iterations))

        if rule_count >= target_rule_count:
            flag = False
            logging.debug(f"Target rule count satisfied: {target_rule_count}")
        else:
            exectime = time.time() - starttime

            if exectime > total_timeout:
                logging.debug(f"Execution time exceeded: {total_timeout}")
                flag = False

            elif (
                maxlen < MAX_RULE_LEN
                and lastrulecount != rule_count
                and not maxlendecreased_due_timeout
            ):
                maxlen += 1
                lastrulecount = rule_count
                logging.debug(f"Increasing maxlen {maxlen}")

            elif (
                maxlen < MAX_RULE_LEN
                and maxlendecreased_due_timeout
                and support <= 1 - supp_step
            ):
                support += supp_step
                maxlen += 1
                lastrulecount = rule_count

                logging.debug(f"Increasing maxlen to {maxlen}")
                logging.debug(f"Increasing minsup to {support}")

                maxlendecreased_due_timeout = False

            elif conf > conf_step:
                conf -= conf_step
                logging.debug(f"Decreasing confidence to {conf}")

            else:
                logging.debug("All options exhausted")
                flag = False

    return rules