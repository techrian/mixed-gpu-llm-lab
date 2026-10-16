const assert=require('assert');const {uniqueLabels}=require('./labels');assert.deepStrictEqual(uniqueLabels([' a ','A',' b','']),['a','b']);console.log('visible tests PASS');
