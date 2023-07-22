#!/usr/bin/env python3

import random
import math
import operator
import ai


def nd6(n):
    return [random.randint(1,6) for i in range(n)]

def check(attribute, skill):
    return sum(map(lambda x: operator.le(x, skill), nd6(attribute)))


class Rule:
    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        if isinstance(other, Rule):
            return self.name == other.name
        return NotImplemented


class Attribute:
    def __init__(self, name, category, value=0, wounds_s=0, wounds_m=0, wounds_k=0):
        self.name = name
        self.category = category
        self.value = value
        self.wounds_s = wounds_s
        self.wounds_m = wounds_m
        self.wounds_k = wounds_k

    def __eq__(self, other):
        if isinstance(other, Attribute):
            return self.name == other.name
        return NotImplemented

    def endOfScene(self):
        self.wounds_s = 0

    def endOfMission(self):
        self.wounds_m = 0

    def endOfKampaign(self):
        self.wounds_k = 0

    def effectiveDice(self):
        return max(0, self.value - self.wounds_s - self.wounds_m - self.wounds_k)


class Skill:
    def __init__(self, name, description="", level=1, cost=7):
        self.name = name
        self.description = description
        self.level = level
        self.cost = cost

    def __eq__(self, other):
        if isinstance(other, Skill):
            return self.name == other.name
        return NotImplemented

skill_fight = Skill("Fighting", "fighting", level=1, cost=2)

class Trait:
    def __init__(self, name, description="", cost=7):
        self.name = name
        self.description = description
        self.cost = cost

    def __eq__(self, other):
        if isinstance(other, Trait):
            return self.name == other.name
        return NotImplemented


class Effect:
    def __init__(self, name, description="", successes=1):
        self.name = name
        self.description = description
        self.successes = successes
effect_damage_physical = Effect("damage_physical")
effect_damage_mental = Effect("damage_mental")
effect_damage_social = Effect("damage_social")
effect_block = Effect("block")


class Maneuver:
    def __init__(self, name, difficulty, effects=[], cost=1):
        self.name = name
        self.difficulty = difficulty
        self.effects = effects
        self.cost = cost

    def __eq__(self, other):
        if isinstance(other, Maneuver):
            return self.name == other.name
        return NotImplemented


class Check:
    def __init__(self, dice: int, skill: Skill, effects: list = [], difficulty: int =0):
        self.dice = dice
        self.skill = skill
        self.effects = []
        self.difficulty = difficulty
        self.advantage = 0
        self.successes = None

    def roll(self):
        dice = self.dice + self.advantage
        skill = self.skill.level
        self.successes = sum(map(lambda x: operator.le(x, skill), nd6(dice)))
        self.successes = min( self.successes, self.dice )
        self.successes -= self.difficulty
        return self.successes

    def isSuccessfull(self):
        if self.successes:
            return self.successes >= 1
        else:
            return self.roll() >= 1


class Game:
    def __init__(self, name, rules=[]):
        self.name = name
        self.rules = rules


class Player:
    def __init__(self, attributes=[5,5,5,5,5,5,5,5], atk_strat=None, dmg_strat=None, armor=0):
        self.str = Attribute("Strength", "Physical", value=attributes[0])
        self.dex = Attribute("Dexterity", "Physical", value=attributes[1])
        self.wil = Attribute("Will", "Mental", value=attributes[2])
        self.int = Attribute("Intelect", "Mental", value=attributes[3])
        self.cha = Attribute("Charisma", "Social", value=attributes[4])
        self.emp = Attribute("Empathy", "Social", value=attributes[5])
        self.gea = Attribute("Gear", "Resources", value=attributes[6])
        self.fin = Attribute("Finanzes", "Resources", value=attributes[7])
        self.skills = [skill_fight]
        self.traits = []
        self.atk_strat = atk_strat or ai.atk_strat_equal_bias_atk
        self.dmg_strat = dmg_strat or ai.dmg_strat_equal_bias_att2_sensible
        self.armor = armor

    def otherAttrInCategory(self, attr):
        for a in [self.str, self.dex, self.wil, self.int, self.cha, self.emp, self.gea, self.fin]:
            if a.category == attr.category:
                return a
        return None

    def fightingAttr(self):
        if self.str.value >= self.dex.value:
            return self.str
        else:
            return self.dex

    def offensiveDice(self):
        attr, _ = self.atk_strat( self.fightingAttr().effectiveDice() )
        return attr

    def defensiveDice(self):
        _, attr = self.atk_strat( self.fightingAttr().effectiveDice() )
        return attr

    def isDead(self):
        for a in [self.str, self.dex, self.wil, self.int, self.cha, self.emp, self.gea, self.fin]:
            if a.effectiveDice() <= 0:
                return True
        return False
        # attr1 = self.fightingAttr()
        # attr2 = self.otherAttrInCategory(attr1)
        # return attr1.effectiveDice() <= 0 or attr2.effectiveDice() <= 0

    def takeDmg(self, n):
        attr1 = self.fightingAttr()
        attr2 = self.otherAttrInCategory(attr1)
        val1 = attr1.effectiveDice()
        val2 = attr2.effectiveDice()
        # attr1 = self.attr1 - self.attr1_wound_s - self.attr1_wound_m
        # attr2 = self.attr2 - self.attr2_wound_s - self.attr2_wound_m
        dmg1_s, dmg2_s = self.dmg_strat(min(self.armor, n), val1, val2)
        # dmg1_s = self.dmg_strat(min(self.armor, n), val1, val2)
        # dmg2_s = max(0, min(self.armor, n) - dmg1_s)
        dmg1_m, dmg2_m = self.dmg_strat(max(0, n - min(self.armor, n)), val1-dmg1_s, val2-dmg2_s)
        # dmg1_m = self.dmg_strat(max(0, n - min(self.armor, n)), attr1-dmg1_s, attr2-dmg2_s)
        # dmg2_m = max(0, n - min(self.armor, n)) - dmg1_m
        attr1.wounds_s += dmg1_s
        attr2.wounds_s += dmg2_s
        attr1.wounds_m += dmg1_m
        attr2.wounds_m += dmg2_m
        # self.attr1_wound_s += dmg1_s
        # self.attr2_wound_s += dmg2_s
        # self.attr1_wound_m += dmg1_m
        # self.attr2_wound_m += dmg2_m

    def offensiveCheck(self):
        return Check(self.offensiveDice(), self.skills[0], effect=effect_damage_physical)

    def defensiveCheck(self):
        return Check(self.defensiveDice(), self.skills[0], effect=effect_block)
