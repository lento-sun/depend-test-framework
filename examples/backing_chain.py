from utils import enter_depend_test, run_cmd, run_shell, STEPS, RESULT, SETUP
enter_depend_test()

from depend_test_framework.test_object import Action, CheckPoint, TestObject, Mist, MistDeadEndException, MistClearException
from depend_test_framework.dependency import Provider, Consumer, Graft, Cut
from depend_test_framework.base_class import ParamsRequire

import random

@Action.decorator(1)
@ParamsRequire.decorator(['guest_name', 'snapshot_round'])
@Consumer.decorator('$guest_name.active', Consumer.REQUIRE)
#@Consumer.decorator('$guest_name.config', Consumer.REQUIRE)
@Consumer.decorator('$guest_name.with_snapshots', Consumer.REQUIRE_N)
@Provider.decorator('$guest_name.with_snapshots', Provider.SET)
def create_snapshot(params, env):
    """
    Create snapshots
    """
    guest = params.guest_name
    snapshot_num = params.snapshot_round
    for num in range(int(snapshot_num)):
        snapshot_name = 'snap_' + str(num)
        cmd = ("virsh snapshot-create-as %s %s --disk-only" %
              (guest, snapshot_name))
        params.logger.info("test:running cmd: %s" % cmd)
        ret = run_shell(cmd)
        params.logger.info("test:cmd_result of '%s' is: %s" % (cmd, str(ret)))


@CheckPoint.decorator(1)
@ParamsRequire.decorator(['guest_name', 'snapshot_round'])
@Consumer.decorator('$guest_name.with_snapshots', Consumer.REQUIRE)
@Consumer.decorator('$guest_name.config', Consumer.REQUIRE)
def check_snapshots(params, env):
    """
    Test: check snapshots
    """
    guest = params.guest_name
    expecting_snapshot_num = int(params.snapshot_round)
    cmd = "virsh snapshot-list %s|grep snap_|wc -l" % guest
    ret = run_shell(cmd)
    params.logger.info("cmd_ret:%s" % str(ret))
#    params.logger.info("cmd_ret:%s cmd_ret_stdout:%s" % (ret, ret.stdout))
#    params.logger.info("cmd_ret:%s cmd_ret_stderr:%s" % (ret, ret.stderr))
#    params.logger.info("Expecting %s snapshots, list %s snapshots" %
#                       (expecting_snapshot_num, existing_snapshot_num))
#    if expecting_snapshot_num == existing_snapshot_num:
#        params.logger.info("check:the snapshots of vm -- pass")
#    else:
#        params.logger.info("check:the snapshots of vm -- failed")

@Action.decorator(1)
@ParamsRequire.decorator(['guest_name'])
@Consumer.decorator('$guest_name.active', Consumer.REQUIRE)
@Consumer.decorator('$guest_name.with_snapshots', Consumer.REQUIRE)
@Cut.decorator('$guest_name.with_snapshots')
def delete_snapshots(params, env):
    """
    Delete snapshots
    """
    guest = params.guest_name
    snapshots = get_snapshots(params, env)
    for snap in snapshots:
        cmd = "virsh snapshot-delete %s %s --metadata" % (guest, bytes.decode(snap))
        ret = run_shell(cmd)
        params.logger.info("test:cmd_result of %s is %s" %
                           (cmd, ret.stdout))
        params.logger.info("test:cmd_err of %s is %s" % (cmd, ret.stderr))
    cmd = "rm /var/lib/libvirt/images/*snap* -f"
    run_shell(cmd)




@Action.decorator(1)
@ParamsRequire.decorator(['guest_name'])
@Consumer.decorator('$guest_name.active', Consumer.REQUIRE)
@Consumer.decorator('$guest_name.with_snapshots', Consumer.REQUIRE)
@Consumer.decorator('$guest_name.with_snapshots.block_pulled', Consumer.REQUIRE_N)
@Consumer.decorator('$guest_name.with_snapshots.block_committed', Consumer.REQUIRE_N)
@Provider.decorator('$guest_name.with_snapshots.block_pulled', Provider.SET)
def block_pull_snapshots(params, env):
    """
    Do snapshots pull
    """
    guest = params.guest_name
    base_layer = params.get("base_layer", 4)
    params.logger.info("The block pull is from layer '%s' to top."
                       % base_layer)
    cmd = ("virsh blockpull %s vda --base vda[%s] --wait"
           % (guest, str(base_layer)))
    ret = run_shell(cmd)
    params.logger.info("test:cmd_result of %s is %s" % (cmd, ret.stdout))
    params.logger.info("test:cmd_err of %s is %s" % (cmd, ret.stderr))


@Action.decorator(1)
@ParamsRequire.decorator(['guest_name'])
@Consumer.decorator('$guest_name.active', Consumer.REQUIRE)
@Consumer.decorator('$guest_name.with_snapshots', Consumer.REQUIRE)
@Provider.decorator('$guest_name.with_snapshots.block_committed', Provider.SET)
def block_commit_snapshots(params, env):
    """
    Do snapshots commit
    """
    guest = params.guest_name
    snapshot_nums = params.get("snapshot_round", 4)
    commit_layer_index = get_random_values(snapshot_nums, 2) 
    base_layer = params.get("base_layer", commit_layer_index[1])
    top_layer = params.get("top_layer", commit_layer_index[0])
    snapshots = get_snapshots(params, env)
    params.logger.info("The block commit is from layer '%s' to '%s'."
                       % (top_layer, base_layer))
    cmd = ("virsh blockcommit %s vda --top vda[%s] --base vda[%s]"
           % (guest, str(top_layer), str(base_layer)))
    ret = run_shell(cmd)
    params.logger.info("test:cmd_result of %s is %s" % (cmd, ret.stdout))
    params.logger.info("test:cmd_err of %s is %s" % (cmd, ret.stderr))
    clean_result = clean_image_with_xattr()
    params.logger.info("clean result: %s" % clean_result)

def get_snapshots(params, env):
    guest = params.guest_name
    cmd = "virsh snapshot-list %s --name" % guest
    snapshots = run_shell(cmd).stdout.strip().split()
    return snapshots

def get_random_values(max_value, number, sort=True):
    """
    :param max_value: Potential max value
    :param number: how many values you required
    :param sort: if return values are sorted
    """
    candidates = list(range(1, max_value + 1))
    picked_values = random.sample(candidates, number)
    if sort:
        picked_values.sort()
    return picked_values

def clean_image_with_xattr(image_path="/var/lib/libvirt/images/test.qcow2"):
    clean_cmd = ("for i in $(getfattr -m trusted.libvirt.security -d %s |"
                 "grep 'trusted.libvirt'| cut -f 1 -d '=');"
                 "do setfattr -x $i %s;done")
    cmd = clean_cmd % (image_path, image_path)
    return run_shell(cmd)

