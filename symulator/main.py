#!/usr/bin/env python3

import random
import math
import operator
import ai
import logging


def nd6(n):
    return [random.randint(1,6) for i in range(n)]

def check(attribute, skill):
    return sum(map(lambda x: operator.le(x, skill), nd6(attribute)))

def cancelOut(n, m):
    h = min(n, m)
    n -= h
    m -= h
    return n, m

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
        self.successes = max(0, self.successes)
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
        self.round = 0

    def simulateCombatRound(self):
        self.round += 1
        logging.info("Simulate Combat Round %s" % self.round)
        player_atks = []
        player_blks = []
        enemy_atks = []
        enemy_blks = []
        for p in self.players:
            checks = p.getCombatChecks()
            for c in checks:
                if c.effect.name == "damage_physical":
                    player_atks.append(c)
                elif c.effect.name == "block":
                    player_blks.append(c)
                else:
                    logging.error('Unknown Effect %s by player %s' % (c.effect.name, p.name))
        for p in self.enemies:
            checks = p.getCombatChecks()
            for c in checks:
                if c.effect.name == "damage_physical":
                    enemy_atks.append(c)
                elif c.effect.name == "block":
                    enemy_blks.append(c)
                else:
                    logging.error('Unknown Effect %s by enemy %s' % (c.effect.name, p.name))
        player_total_atks = 0
        for c in player_atks:
            player_total_atks += c.roll()
        player_total_blks = 0
        for c in player_blks:
            player_total_blks += c.roll()
        enemy_total_atks = 0
        for c in enemy_atks:
            enemy_total_atks += c.roll()
        enemy_total_blks = 0
        for c in enemy_blks:
            enemy_total_blks += c.roll()
        player_total_atks, enemy_total_blks = cancelOut(player_total_atks, enemy_total_blks)
        enemy_total_atks, player_total_blks = cancelOut(enemy_total_atks, player_total_blks)
        player_total_blks, enemy_total_blks = cancelOut(player_total_blks, enemy_total_blks)
        player_dmg = player_total_atks*2+player_total_blks
        enemy_dmg = enemy_total_atks*2+enemy_total_blks
        logging.debug("Character %s\ttakes %s damage" % (self.players[0].name, enemy_dmg))
        self.players[0].takeDmg(enemy_dmg)
        logging.debug("Character %s\ttakes %s damage" % (self.enemies[0].name, player_dmg))
        self.enemies[0].takeDmg(player_dmg)
        for c in self.players + self.enemies:
            if c.isDead():
                logging.debug("Character %s died" % (c.name))

    def removeDead(self):
        ret = False
        for c in self.players:
            if c.isDead():
                self.players.remove(c)
                ret = True
        for c in self.enemies:
            if c.isDead():
                self.enemies.remove(c)
                ret = True
        return ret

    def endOfScene(self):
        for c in self.players + self.enemies:
            c.endOfScene()

    def endOfMission(self):
        for c in self.players + self.enemies:
            c.endOfMission()

    def endOfKampaign(self):
        for c in self.players + self.enemies:
            c.endOfKampaign()

class Player:
    def __init__(self, attributes=[5,5,5,5,5,5,5,5], atk_strat=None, armor=0, name=""):
        self.name = name
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
        val = attr.effectiveDice()
        cat.wounds_s += min(self.armor, n)
        cat.wounds_m += max(0, n - min(self.armor, n))

    def getCombatChecks(self):
        return [ self.offensiveCheck(), self.defensiveCheck() ]

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

# Script
logging.basicConfig(filename='game.log',
                    encoding='utf-8',
                    filemode='w',
                    level=logging.DEBUG,
                    format='%(levelname)s:\t%(message)s')
g = Game("Game1")
g.players.append( Player(name="Player 1", attributes=[6,6,6,6,6,6,6,6], atk_strat=None, armor=2) )
g.players.append( Player(name="Player 2", attributes=[6,6,6,6,6,6,6,6], atk_strat=None, armor=2) )
g.enemies.append( Player(name="Enemy 1",  attributes=[4,4,4,4,4,4,4,4], atk_strat=None, armor=0) )
g.enemies.append( Player(name="Enemy 2",  attributes=[4,4,4,4,4,4,4,4], atk_strat=None, armor=0) )
g.enemies.append( Player(name="Enemy 3",  attributes=[4,4,4,4,4,4,4,4], atk_strat=None, armor=0) )

for i in range(1,99):
    g.simulateCombatRound()
    if g.removeDead():
        g.endOfScene()
    if len(g.players) == 0 or len(g.enemies) == 0:
        break
if len(g.players) > 0:
    print("Players win")
elif len(g.enemies) > 0:
    print("Enemies win")
else:
    print("Draw")

