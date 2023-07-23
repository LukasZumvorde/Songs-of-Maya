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


class AttributeCategory:
    def __init__(self, name, wounds_s=0, wounds_m=0, wounds_k=0):
        self.name = name
        self.wounds_s = wounds_s
        self.wounds_m = wounds_m
        self.wounds_k = wounds_k
        self.attributes = []

    def endOfScene(self):
        self.wounds_s = 0

    def endOfMission(self):
        self.wounds_m = 0

    def endOfKampaign(self):
        self.wounds_k = 0


class Attribute:
    def __init__(self, name, category, value=0, wounds_s=0, wounds_m=0, wounds_k=0):
        self.name = name
        self.category = category
        self.value = value

    def __eq__(self, other):
        if isinstance(other, Attribute):
            return self.name == other.name
        return NotImplemented

    def effectiveDice(self):
        return max(0, self.value - self.category.wounds_s - self.category.wounds_m - self.category.wounds_k)


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
        self.target = None
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
    def __init__(self, dice: int, skill: Skill, effect: Effect, difficulty: int =0):
        self.dice = dice
        self.skill = skill
        self.effect = effect
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
        self.players = []
        self.enemies = []

    def simulateCombatRound(self):
        player_atks = []
        player_blks = []
        enemie_atks = []
        enemie_blks = []
        for p in players:
            checks = p.getCombatChecks()
            for c in checks:
                if c.effect.name == "damage_physical":
                    player_atks.append(c)
                if c.effect.name == "block":
                    player_blks.append(c)
        for p in enemies:
            checks = p.getCombatChecks()
            for c in checks:
                if c.effect.name == "damage_physical":
                    enemie_atks.append(c)
                if c.effect.name == "block":
                    enemie_blks.append(c)
        

class Player:
    def __init__(self, attributes=[5,5,5,5,5,5,5,5], atk_strat=None, armor=0):
        self.physical  = AttributeCategory("Physical")
        self.mental    = AttributeCategory("Mental")
        self.social    = AttributeCategory("Social")
        self.resources = AttributeCategory("Resources")
        self.categories = [self.physical, self.mental, self.social, self.resources]
        self.str = Attribute("Strength",  self.physical, value=attributes[0])
        self.dex = Attribute("Dexterity", self.physical, value=attributes[1])
        self.wil = Attribute("Will",      self.mental, value=attributes[2])
        self.int = Attribute("Intelect",  self.mental, value=attributes[3])
        self.cha = Attribute("Charisma",  self.social, value=attributes[4])
        self.emp = Attribute("Empathy",   self.social, value=attributes[5])
        self.gea = Attribute("Gear",      self.resources, value=attributes[6])
        self.fin = Attribute("Finanzes",  self.resources, value=attributes[7])
        self.physical.attributes.append(self.str)
        self.physical.attributes.append(self.dex)
        self.mental.attributes.append(self.wil)
        self.mental.attributes.append(self.int)
        self.social.attributes.append(self.cha)
        self.social.attributes.append(self.emp)
        self.resources.attributes.append(self.gea)
        self.resources.attributes.append(self.fin)
        self.attributes = [self.str, self.dex, self.wil, self.int, self.cha, self.emp, self.gea, self.fin]
        self.skills = [skill_fight]
        self.traits = []
        self.atk_strat = atk_strat or ai.atk_strat_equal_bias_atk
        self.armor = armor
        self.states = []

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

    def takeDmg(self, n):
        attr = self.fightingAttr()
        cat = attr.category
        val = attr1.effectiveDice()
        cat.wounds_s += min(self.armor, n)
        cat.wounds_m += max(0, n - min(self.armor, n))

    def getCombatChecks(self, game):
        return [ self.offensiveCheck(), self.defensiveCheck(self) ]

    def offensiveCheck(self):
        return Check(self.offensiveDice(), self.skills[0], effect=effect_damage_physical)

    def defensiveCheck(self):
        return Check(self.defensiveDice(), self.skills[0], effect=effect_block)

    def endOfScene(self):
        for cat in self.categories:
            cat.endOfScene()

    def endOfMission(self):
        for cat in self.categories:
            cat.endOfMission()

    def endOfKampaign(self):
        for cat in self.categories:
            cat.endOfKampaign()
