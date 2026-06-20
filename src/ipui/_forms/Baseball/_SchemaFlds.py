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

    FIELDS = [

        'Key      pa        INTEGER  plate appearance',
        'Entity   b         INTEGER  batter',
        'Entity   p         INTEGER  pitcher',
        'Key      pitcher   INTEGER  pitcher',
        'Key      batter    INTEGER  batter id',
        'Metric   ab        INTEGER  at bat',
        'Metric   h         INTEGER  hit',
        'Metric   k         INTEGER  strikeout',
        'Context  vsL       INTEGER  versus Lefthander',
        'Context  vsR       INTEGER  versus Right',
        'Metric   ba        REAL     batting average',
        'Metric   z         REAL     made up metric',
    ]