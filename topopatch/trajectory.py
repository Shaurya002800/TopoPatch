"""Run migration until all objects are migrated or no safe action is found."""
from .engine import Engine

def migrate(fixture):
    engine=Engine(); engine.initialize(fixture); steps=[]
    for _ in range(len(fixture['documents'])):
        remaining=[r['id'] for r in engine.rows() if r['active']=='A']
        if not remaining: break
        proposal=engine.propose()
        action=proposal['recommended']
        if action:
            manifest=engine.commit(action['preview_id'])
            steps.append({'strategy':'selective','epoch':manifest['epoch'],'ids':manifest['ids']})
        else:
            # Explicit full-remainder expansion; all new work is charged.
            p=engine.preview(remaining)
            if not p['barrier']['pass']:
                steps.append({'strategy':'halt','reason':'Full-target state violates protected constraints'})
                break
            manifest=engine.commit(p['id'])
            steps.append({'strategy':'full_remainder','epoch':manifest['epoch'],'ids':manifest['ids']})
    return {'steps':steps,'complete':engine.status()['active_b']==len(fixture['documents']), 'evidence':engine.export()}
