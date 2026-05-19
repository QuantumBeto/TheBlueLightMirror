# core/mission_manager.py
class MissionManager:
    def __init__(self, stage_id):
        self.stage_id = stage_id
        self.missions = {}
        self.completed = set()
        self.active = set()
    
    def register(self, mission_list):
        for m in mission_list:
            self.missions[m["id"]] = m
            self.active.add(m["id"])
    
    def check_triggers(self, player):
        for mid in list(self.active):
            m = self.missions[mid]
            trigger_type, *args = m["trigger"].split(":")
            if self._evaluate_trigger(trigger_type, args, player):
                self._complete(mid, player)
    
    def _evaluate_trigger(self, ttype, args, player):
        if ttype == "interact_object":
            return player.last_interaction == args[0]
        if ttype == "collect_item":
            return args[0] in player.inventory
        if ttype == "enter_zone":
            return player.current_zone == args[0]
        if ttype == "timer_in_zone":
            zone, seconds = args[0], float(args[1])
            return player.time_in_zone.get(zone, 0) >= seconds
        if ttype == "interact_npc":
            npc_id, condition = args[0], args[1]
            if condition == "no_device":
                return player.last_npc == npc_id and not player.device_equipped
        return False
    
    def _complete(self, mission_id, player):
        m = self.missions[mission_id]
        self.active.discard(mission_id)
        self.completed.add(mission_id)
        for stat, delta in m.get("reward", {}).items():
            player.stats[stat] = player.stats.get(stat, 0) + delta
        # Emite evento para el HUD
        player.events.emit("MISSION_COMPLETE", m)
    
    def get_status(self):
        return {
            "total": len(self.missions),
            "completed": len(self.completed),
            "active": [self.missions[m] for m in self.active]
        }