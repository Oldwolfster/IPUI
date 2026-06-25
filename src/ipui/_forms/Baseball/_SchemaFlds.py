class _SchemaFlds:
    """Source-of-truth mirror of the _registry table's hand-entered vocab rows.
       Same role for _registry's DATA as _SchemaTbl plays for every table's SHAPE --
       always exists, even empty, and is never touched by a DB drop.

       Either side can add a field: the DB tab's Save/Delete write here too
       (MgrBackup.save_field / delete_field), and BbDB.configure() pulls any
       hand-typed line here into _registry on startup (MgrBackup.sync_fields_to_db),
       inserting only what's missing -- existing (kind, token) rows are never touched.

       Each entry is one aligned string: 'kind     token     dtype    definition'.
       kind/token/dtype can never contain a space, so they're always the line's first
       3 whitespace tokens; the definition is everything after -- free text, spaces and all."""


    # _SchemaFlds.py  Update: remove GD, it's auto-injected
    FIELDS = [

        'Key      game      INTEGER  20    game id (primary key)',
        'Key      TS        INTEGER  24    time slice (200 season)',
        'Key      batter    INTEGER  30    batter id',
        'Key      pitcher   INTEGER  41    pitcher id',
        'Key      pa        INTEGER  50    plate appearance - at bat number',
        'Entity   b         INTEGER  500   batter',
        'Entity   p         INTEGER  500   pitcher',
        'Metric   ab        INTEGER  1000  at bat',
        'Metric   h         INTEGER  1000  hit',
        'Metric   k         INTEGER  1000  strikeout',
        'Metric   ba        REAL     1000  batting average',
        'Metric   z         REAL     1000  made up metric',
        'Context  vsL       INTEGER  5000  versus Lefthander',
        'Context  vsR       INTEGER  5000  versus Right',

        'Key      testKey   INTEGER  50    test',
    ]