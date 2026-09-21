"""Paste-ready broadleaf replacement for project/scripts/site.py::_tree_asset.

Uses the existing site's math, Vector, _tube, _leaf, _data_mesh and
_leaf_material symbols. Does not import or mutate the integrated site module.
The generator is photograph-informed landscape approximation (evidence C).

Revision 2 replaces individually capped branch segments with continuous
shared-ring curves and smooth bark shading. Fork attachments are staggered
along the bole; broad, lower crowns replace the previous upright profile.
Blender 5.2.1 LTS nonrender smoke on 2026-09-20 passed six seed/variant builds:
detailed 15,552/20,736 leaves and 119,222/158,846 vertices; far 5,040/6,720
leaves and 40,070/53,339 vertices. Detailed sample crown widths are 12.64 and
14.49 m, leaf bases 5.83 and 5.86 m. Small sample assets are 4.41/7.49 m
high with 2,880/4,320 leaves. Smooth bark, finite vertices, leaf UV and
170,000-vertex / 7,000-background-leaf budgets passed assertions.
Integration and rendered appearance remain the scene integrator's
responsibility; no photorealism gate is claimed.
"""


def _tree_asset(ctx, rng, index, detail=True, small=False):
    barkv, barkf, leafv, leaff, indices = [], [], [], [], []
    H = rng.uniform(12.0, 19.0) if not small else rng.uniform(4.2, 7.6)
    radius = H * rng.uniform(.018, .024)
    fork_height = H * rng.uniform(.22, .34) if not small else H * rng.uniform(.15, .25)
    fork_count = rng.choice((3, 4)) if not small else rng.choice((2, 3))
    drift = Vector((rng.uniform(-.55, .55), rng.uniform(-.48, .48), 0))
    turn = rng.uniform(0, TAU)

    def curve(a, b, c, t):
        return a * ((1-t)**2) + b * (2*t*(1-t)) + c * (t*t)

    def woody_curve(a, b, c, start_radius, end_radius, segments, sides):
        # One ring is shared across each adjacent pair of segments. The frame
        # follows the curve by its minimum tangent rotation, avoiding the
        # independently capped cylinders and visible staircase collars.
        first = len(barkv)
        previous_tangent = None
        normal = None
        for n in range(segments+1):
            t = n / segments
            point = curve(a, b, c, t)
            tangent = (2*(1-t)*(b-a) + 2*t*(c-b)).normalized()
            if tangent.length < 1e-6:
                tangent = (c-a).normalized()
            if previous_tangent is None:
                helper = Vector((0, 0, 1)) if abs(tangent.z) < .9 else Vector((0, 1, 0))
                normal = tangent.cross(helper).normalized()
            else:
                normal = previous_tangent.rotation_difference(tangent) @ normal
                normal = (normal-tangent*normal.dot(tangent)).normalized()
            binormal = tangent.cross(normal).normalized()
            radius_here = end_radius+(start_radius-end_radius)*((1-t)**1.12)
            for j in range(sides):
                angle = j*TAU/sides
                barkv.append(tuple(point+radius_here*(normal*math.cos(angle)+binormal*math.sin(angle))))
            if n:
                lower = first+(n-1)*sides
                upper = first+n*sides
                for j in range(sides):
                    after = (j+1)%sides
                    barkf.append((lower+j, lower+after, upper+after, upper+j))
            previous_tangent = tangent
        # Caps exist only at the two ends of the whole continuous curve.
        barkf.append(tuple(first+j for j in reversed(range(sides))))
        barkf.append(tuple(first+segments*sides+j for j in range(sides)))

    # A short, bending bole ends at the crotch. There is NO upright central
    # leader continuing to the crown tip, and no spiral of radial branch tiers.
    base = Vector((0, 0, 0))
    crotch = drift + Vector((0, 0, fork_height+H*.08))
    bend = drift * -.28 + Vector((rng.uniform(-.18, .18), rng.uniform(-.18, .18), crotch.z*.46))
    woody_curve(base, bend, crotch, radius*1.16, radius*.48, 12, 14 if detail else 11)
    for root in range(6):
        theta = turn + root*TAU/6 + rng.uniform(-.32, .32)
        spread = radius*rng.uniform(3.7, 6.1)
        end = Vector((math.cos(theta)*spread, math.sin(theta)*spread, .015))
        elbow = end*.48 + Vector((0, 0, radius*.24))
        woody_curve(base+Vector((0, 0, radius*.70)), elbow, end,
                    radius*rng.uniform(.25, .41), .013, 3, 7 if detail else 5)

    # Different crown heights, unequal horizontal reach and unequal branch
    # thickness keep the lobes asymmetric. One lobe sets the reported height.
    lobes = []
    tallest = rng.randrange(fork_count)
    first_fork_actual = H
    for j in range(fork_count):
        theta = turn + j*TAU/fork_count + rng.uniform(-.45, .45)
        radial = Vector((math.cos(theta), math.sin(theta), 0))
        tangent = Vector((-radial.y, radial.x, 0))
        reach = H*rng.uniform(.22, .34) * (.92 if small else 1)
        top = H*(.915 if j == tallest else rng.uniform(.69, .88))
        # Unequal insertion heights avoid several equal limbs meeting as a Y.
        insertion = .67 + .29*j/max(1, fork_count-1) + rng.uniform(-.035, .025)
        attachment = curve(base, bend, crotch, insertion)
        first_fork_actual = min(first_fork_actual, attachment.z)
        parent_radius = radius*.48+(radius*1.16-radius*.48)*((1-insertion)**1.12)
        # Sink the start and its end cap inside the parent bole.
        fork_start = attachment-radial*parent_radius*.30
        endpoint = attachment + radial*reach + tangent*rng.uniform(-.8, .8)
        endpoint.z = top
        control = attachment + radial*reach*rng.uniform(.20, .52)
        control += tangent*rng.uniform(-.55, .55)
        control.z = attachment.z+(top-attachment.z)*rng.uniform(.37, .63)
        branch_radius = min(parent_radius*.86, radius*rng.uniform(.70, .91)/math.sqrt(fork_count))
        woody_curve(fork_start, control, endpoint, branch_radius, .016 if not small else .007,
                    11 if detail else 8, 12 if detail else 9)
        lobes.append((fork_start, control, endpoint, radial, tangent, branch_radius))

    scaffold_count = 8 if detail and not small else (6 if small else 7)
    shoot_count = 9 if detail and not small else 6
    twig_count = 3 if detail and not small else 2
    leaf_nodes = 12 if detail and not small else 10
    # Maximum detailed case: 4 * 8 * 9 * 3 * 12 * 2 = 20,736 leaves.
    # Maximum far case: 4 * 7 * 6 * 2 * 10 * 2 = 6,720 leaves.
    for a, b, c, radial, tangent, fork_radius in lobes:
        for k in range(scaffold_count):
            t = .20 + .77*(k+rng.uniform(.08, .87))/scaffold_count
            start = curve(a, b, c, t)
            # Unordered local directions, rather than golden-angle trunk whorls.
            yaw = rng.uniform(-2.5, 2.5)
            direction = radial*math.cos(yaw) + tangent*math.sin(yaw)
            span = H*rng.uniform(.105, .175) * (.98 if small else 1)
            # Crown shoulders remain broad at the top; no conical falloff.
            end = start + direction*span + Vector((0, 0, span*rng.uniform(-.09, .35)))
            end.z = min(end.z, H*.94)
            elbow = start.lerp(end, .50) + tangent*rng.uniform(-.25, .25)
            elbow.z -= span*rng.uniform(.02, .12)
            parent_radius = .016+(fork_radius-.016)*((1-t)**1.12)
            r0 = max(.014, parent_radius*rng.uniform(.27, .43))
            buried_start = start-direction*parent_radius*.45
            woody_curve(buried_start, elbow, end, r0, .007 if not small else .003,
                        5, 8 if detail else 6)
            along = (end-start).normalized()
            across = Vector((-along.y, along.x, 0)).normalized()
            for s in range(shoot_count):
                u = rng.uniform(.26, .99)
                origin = curve(start, elbow, end, u)
                side = -1 if s % 2 else 1
                shoot_dir = (along*rng.uniform(.22, .70) + across*side*rng.uniform(.35, .95)
                             + Vector((0, 0, rng.uniform(-.18, .58)))).normalized()
                shoot_length = rng.uniform(.70, 1.28)*(H/15 if not small else H/6*.76)
                shoot_end = origin + shoot_dir*shoot_length
                # Leafy fans have distinct nodal shoots and twigs, not filled
                # sphere meshes or scattered leaves floating around a volume.
                shoot_mid = origin.lerp(shoot_end, .50) + Vector((0, 0, -.045*shoot_length))
                woody_curve(origin, shoot_mid, shoot_end, .007 if not small else .004,
                            .0027 if not small else .0017, 2, 5 if detail else 4)
                local_side = Vector((-shoot_dir.y, shoot_dir.x, 0)).normalized()
                for q in range(twig_count):
                    v = .36 + .62*(q+rng.uniform(.15, .85))/twig_count
                    twig_start = curve(origin, shoot_mid, shoot_end, v)
                    sign = -1 if q % 2 else 1
                    twig_dir = (shoot_dir*.47 + local_side*sign*rng.uniform(.40, .90)
                                + Vector((0, 0, rng.uniform(-.32, .40)))).normalized()
                    length = rng.uniform(.44, .69)*(H/15 if not small else H/6*.95)
                    twig_end = twig_start + twig_dir*length
                    _tube(barkv, barkf, twig_start, twig_end,
                          .0031 if not small else .0021, .00085, 4)
                    leaf_axis = Vector((-twig_dir.y, twig_dir.x, 0)).normalized()
                    for n in range(leaf_nodes):
                        w = (n+.30+rng.uniform(0, .22))/leaf_nodes
                        node = twig_start.lerp(twig_end, w)
                        for sign in (-1, 1):
                            leaf_dir = (leaf_axis*sign + twig_dir*rng.uniform(.15, .70)
                                        + Vector((0, 0, rng.uniform(-.43, .26)))).normalized()
                            # 11–19 cm blades in the detailed forest. Background
                            # blades remain below 22 cm rather than giant cards.
                            leaf_length = rng.uniform(.11, .19)*(1 if detail else 1.12)
                            if small:
                                leaf_length *= .88
                            petiole = node + twig_dir*rng.uniform(-.025, .025)
                            center = petiole + leaf_dir*leaf_length*.39
                            _leaf(leafv, leaff, indices, center, leaf_dir, leaf_length,
                                  leaf_length*rng.uniform(.65, .88), rng)

    bark = _data_mesh(f'TREE_Asset_{index}_Woody_Branches', barkv, barkf, [ctx.mats['bark']])
    for polygon in bark.polygons:
        polygon.use_smooth = True
    foliage = _data_mesh(f'TREE_Asset_{index}_Individual_Leaves', leafv, leaff,
                        [_leaf_material(ctx, key) for key in ('leaf', 'leaf_dark', 'leaf_light')], indices)
    # Useful both for integration QA and asset-budget inspection.
    bark['growth_form'] = 'forked broadleaf: irregular branch-supported crown lobes'
    bark['major_forks'] = fork_count
    bark['first_fork_height_m'] = first_fork_actual
    bark['branch_mesh_method'] = 'continuous shared rings with minimum-rotation frames; end caps only'
    foliage['individual_leaf_count'] = len(leafv)//7
    foliage['vertex_budget_including_bark'] = len(leafv)+len(barkv)
    foliage['no_foliage_blobs'] = True
    actual_height = max(vertex[2] for vertex in barkv + leafv)
    return bark, foliage, actual_height
