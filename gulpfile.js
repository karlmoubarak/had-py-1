// gulpfile.js

// gulp-packages
var gulp = require('gulp');
var del =  require('del');
var concat = require('gulp-concat');
var rename = require('gulp-rename');

var postcss = require('gulp-postcss');
var cssnext = require('postcss-cssnext');
var nano = require('gulp-cssnano');
var atImport = require('postcss-import');

var jshint = require('gulp-jshint');
var uglify = require('gulp-uglify');
var livereload = require('gulp-livereload');
var notify = require("gulp-notify");
var inlinesource = require('gulp-inline-source');

gulp.task('clean', function () {
	return del([
		'assets/dist/**/*']);
});

// Styles
var processors = [
	atImport,
	cssnext({
		'browsers': ['last 2 version'],
		'features': {
			'customProperties': {
				preserve: true,
				appendVariables: true
			},
			'colorFunction': true,
			'customSelectors': true,
			'rem': false
		}
	})
];

//export also non-minified version? makes no sense with sourcemap version?
gulp.task('styles', function(){
	return gulp.src('assets/src/css/style.css')
	.pipe(postcss(processors))
	.pipe(gulp.dest('assets/dist/css'))
	.pipe(nano({discardComments: {removeAll: true}}))
	.pipe(rename({
		suffix: '.min'
	}))
	.pipe(gulp.dest('assets/dist/css'))
	.pipe(notify({ message: 'Styles task complete' }));
});

// Concatenate & Minify JS ::collection
gulp.task('scripts:collection', function() {
	return gulp.src('assets/src/js/collection/*.js')
	.pipe(jshint())
	.pipe(jshint.reporter('default'))
	.pipe(concat('collection.js'))
	.pipe(gulp.dest('assets/dist/js/')) // non-minified js file
	.pipe(rename({
		suffix: '.min'
	}))
	.pipe(uglify())
	.pipe(gulp.dest('assets/dist/js/'))
	.pipe(notify({ message: 'Scripts task complete' }));
});

// Scripts
gulp.task('scripts', ['scripts:collection']);

gulp.task('watch', function() {

  // Watch .css files
  gulp.watch('assets/src/css/*.css', ['styles']);

  // Watch .js files
  gulp.watch('assets/src/js/**/*.js', ['scripts']);

  // Create LiveReload server
  livereload.listen();

  // Watch any files in dist/, reload on change
  gulp.watch(['assets/dist/**']).on('change', livereload.changed);
});

// Default Task
gulp.task('default', ['clean', 'styles', 'scripts', 'watch']);
