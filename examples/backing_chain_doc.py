from utils import enter_depend_test, STEPS, RESULT, SETUP
enter_depend_test()

from depend_test_framework.test_object import Mist, MistDeadEndException, MistClearException
from depend_test_framework.dependency import Provider, Consumer

def create_snapshot(params, env):
    """
    Create snapshot for vm
    """
    cmd_pattern = "virsh snapshot-create-as %s %s --disk-only"
    for num in range(int(params.snapshot_round)):
        cmd = cmd_pattern % (params.guest_name, "snap_" + str(num))
        params.doc_logger.info(STEPS + """
            running cmd %s
            """
            % cmd)

def check_snapshots(params, env):
    """
    Check snapshot for vm
    """
    cmd = "virsh snapshot-list " + params.guest_name
    params.doc_logger.info(STEPS + """
        running cmd %s
        """
        % cmd)

def delete_snapshots(params, env):
    """
    Delete snapshots for vm
    """
    cmd_pattern = "virsh snapshot-delete %s %s --metadata"
    for num in range(int(params.snapshot_round)):
        cmd = cmd_pattern % (params.guest_name, "snap_" + str(num))
        params.doc_logger.info(STEPS + """
            running cmd %s
            """
            % cmd)

def block_commit(params, env):
    pass

def block_pull(params, env):
    pass

def block_copy(params, env):
    pass

