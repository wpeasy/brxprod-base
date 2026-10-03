// Read-only design-system extract for /design-system. Runs via novamira/execute-php.
// Returns raw site data as JSON; render.py does all filtering and formatting.
// Do NOT add writes here: generate.sh runs this with --yes and no prompt.

if ( ! function_exists( 'get_plugins' ) ) {
	require_once ABSPATH . 'wp-admin/includes/plugin.php';
}

$names_by_id = function ( $option ) {
	$out = [];
	foreach ( (array) get_option( $option, [] ) as $c ) {
		if ( isset( $c['id'] ) ) {
			$out[ $c['id'] ] = $c['name'] ?? $c['id'];
		}
	}
	return $out;
};

$var_cats   = $names_by_id( 'bricks_global_variables_categories' );
$class_cats = $names_by_id( 'bricks_global_classes_categories' );

$variables = [];
foreach ( (array) get_option( 'bricks_global_variables', [] ) as $v ) {
	if ( empty( $v['name'] ) ) {
		continue;
	}
	$variables[] = [
		'name'     => $v['name'],
		'value'    => isset( $v['value'] ) ? (string) $v['value'] : '',
		'category' => $var_cats[ $v['category'] ?? '' ] ?? '',
	];
}

$palettes = [];
foreach ( (array) get_option( 'bricks_color_palette', [] ) as $p ) {
	$colors = [];
	foreach ( (array) ( $p['colors'] ?? [] ) as $c ) {
		$colors[] = [
			'name' => $c['name'] ?? '',
			'raw'  => $c['raw'] ?? '',
			'hex'  => $c['hex'] ?? '',
		];
	}
	$palettes[] = [ 'name' => $p['name'] ?? '', 'colors' => $colors ];
}

$classes = [];
foreach ( (array) get_option( 'bricks_global_classes', [] ) as $c ) {
	if ( empty( $c['name'] ) ) {
		continue;
	}
	$classes[] = [
		'name'     => $c['name'],
		'category' => $class_cats[ $c['category'] ?? '' ] ?? '',
		'locked'   => ! empty( $c['locked'] ),
	];
}

$theme_styles = [];
foreach ( (array) get_option( 'bricks_theme_styles', [] ) as $id => $s ) {
	$theme_styles[] = [
		'id'         => $id,
		'label'      => $s['label'] ?? $id,
		'conditions' => array_map(
			function ( $c ) { return $c['main'] ?? '?'; },
			(array) ( $s['settings']['conditions']['conditions'] ?? [] )
		),
	];
}

$all_plugins = get_plugins();
$active      = [];
foreach ( (array) get_option( 'active_plugins', [] ) as $file ) {
	$active[] = [
		'file'    => $file,
		'name'    => $all_plugins[ $file ]['Name'] ?? $file,
		'version' => $all_plugins[ $file ]['Version'] ?? '',
	];
}

global $wpdb;
// Core Framework support is unverified: record its footprint so the renderer
// (and whoever finishes that branch) can see where its tokens live.
$cf_options = $wpdb->get_col(
	"SELECT option_name FROM {$wpdb->options} WHERE option_name LIKE 'core\\_framework%' OR option_name LIKE 'cf\\_%' LIMIT 50"
);

$theme = wp_get_theme();

return [
	'site'         => [
		'url'       => home_url( '/' ),
		'name'      => get_bloginfo( 'name' ),
		'wordpress' => get_bloginfo( 'version' ),
		'bricks'    => defined( 'BRICKS_VERSION' ) ? BRICKS_VERSION : null,
		'theme'     => $theme->get( 'Name' ) . ' ' . $theme->get( 'Version' ),
	],
	'plugins'      => $active,
	'variables'    => $variables,
	'palettes'     => $palettes,
	'classes'      => $classes,
	'themeStyles'  => $theme_styles,
	'coreFrameworkOptions' => $cf_options,
	'generatedAt'  => gmdate( 'c' ),
];
