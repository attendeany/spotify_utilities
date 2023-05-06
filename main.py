from features.collect_tracks.database_filler import fill_artists_info, fill_saved_tracks, fill_track_features

print(f'Saved {fill_saved_tracks()}')
print(f'New artists {fill_artists_info()}')
print(f'New features {fill_track_features()}')
