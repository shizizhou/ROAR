from ROAR.agent_module.agent import Agent
from pathlib import Path
from ROAR.control_module.mpc_controller import VehicleMPCController
from ROAR.planning_module.local_planner \
    .simple_waypoint_following_local_planner import \
    SimpleWaypointFollowingLocalPlanner
from ROAR.planning_module.behavior_planner.behavior_planner import BehaviorPlanner
from ROAR.planning_module.mission_planner.waypoint_following_mission_planner import  WaypointFollowingMissionPlanner
from ROAR.utilities_module.data_structures_models import SensorsData
from ROAR.utilities_module.vehicle_models import VehicleControl, Vehicle
import logging
from ROAR.visualization_module.visualizer import Visualizer


class MPCAgent(Agent):
    def __init__(self, target_speed=40, **kwargs):
        super().__init__(**kwargs)
        self.logger = logging.getLogger("PathFollowingAgent")
        self.mpc_controller = VehicleMPCController(
            agent=self,
            route_file_path=Path(
                self.agent_settings.waypoint_file_path),
            target_speed=target_speed)
        self.mission_planner = WaypointFollowingMissionPlanner(
            agent=self)
        # initiated right after mission plan

        self.behavior_planner = BehaviorPlanner(agent=self)
        self.local_planner = SimpleWaypointFollowingLocalPlanner(
            agent=self,
            controller=self.mpc_controller,
            mission_planner=self.mission_planner,
            behavior_planner=self.behavior_planner,
            closeness_threshold=1)
        self.visualizer = Visualizer(agent=self)
        self.logger.debug(f"Waypoint Following Agent Initiated. "
                          f"Reading from "
                          f"{self.agent_settings.waypoint_file_path}")
        self.curr_max_err = 0
        self.counter = 0
        self.total_err = 0

    def run_step(self, vehicle: Vehicle,
                 sensors_data: SensorsData) -> VehicleControl:
        super(MPCAgent, self).run_step(vehicle=vehicle,
                                       sensors_data=sensors_data)
        self.transform_history.append(self.vehicle.transform)
        if self.local_planner.is_done():
            control = VehicleControl()
            self.logger.debug("Path Following Agent is Done. Idling.")
        else:
            control = self.local_planner.run_in_series()
        return control
