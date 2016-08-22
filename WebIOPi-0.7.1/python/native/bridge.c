/*
Copyright (c) 2012 Ben Croston / 2012-2013 Eric PTAK

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/

#include "Python.h"
#include "gpio.h"
#include "cpuinfo.h"

static PyObject *_SetupException;
static PyObject *_InvalidDirectionException;
static PyObject *_InvalidChannelException;
static PyObject *_InvalidPullException;

static PyObject *_gpioCount;


static PyObject *_low;
static PyObject *_high;

static PyObject *_in;
static PyObject *_out;
static PyObject *_alt0;
static PyObject *_alt1;
static PyObject *_alt2;
static PyObject *_alt3;
static PyObject *_alt4;
static PyObject *_alt5;
static PyObject *_pwm;

static PyObject *_pud_off;
static PyObject *_pud_up;
static PyObject *_pud_down;

static PyObject *_board_revision;

static char* FUNCTIONS[] = {"IN", "OUT", "ALT5", "ALT4", "ALT0", "ALT1", "ALT2", "ALT3", "PWM"};
static char* PWM_MODES[] = {"none", "ratio", "angle"};

static int module_state = -1;

// setup function run on import of the RPi.GPIO module
static int module_setup(void)
{
	if (module_state == SETUP_OK) {
		return SETUP_OK;
	}

	module_state = setup();
	if (module_state == SETUP_DEVMEM_FAIL)
	{
		PyErr_SetString(_SetupException, "No access to /dev/mem.  Try running as root!");
	} else if (module_state == SETUP_MALLOC_FAIL) {
		PyErr_NoMemory();
	} else if (module_state == SETUP_MMAP_FAIL) {
		PyErr_SetString(_SetupException, "Mmap failed on module import");
	}

	return module_state;
}

// python function getFunction(channel)
static PyObject *py_get_function(PyObject *self, PyObject *args)
{
	if (module_setup() != SETUP_OK) {
		return NULL;
	}

	int channel, f;

	if (!PyArg_ParseTuple(args, "i", &channel))
		return NULL;

	if (channel < 0 || channel >= GPIO_COUNT)
	{
		PyErr_SetString(_InvalidChannelException, "The GPIO channel is invalid");
		return NULL;
	}

	f = get_function(channel);
	return Py_BuildValue("i", f);
}

// python function getFunctionString(channel)
static PyObject *py_get_function_string(PyObject *self, PyObject *args)
{
	if (module_setup() != SETUP_OK) {
		return NULL;
	}

	int channel, f;
	char *str;

	if (!PyArg_ParseTuple(args, "i", &channel))
		return NULL;

	if (channel < 0 || channel >= GPIO_COUNT)
	{
		PyErr_SetString(_InvalidChannelException, "The GPIO channel is invalid");
		return NULL;
	}

	f = get_function(channel);
	str = FUNCTIONS[f];
	return Py_BuildValue("s", str);
}

// python function setFunction(channel, direction, pull_up_down=PUD_OFF)
static PyObject *py_set_function(PyObject *self, PyObject *args, PyObject *kwargs)
{
	if (module_setup() != SETUP_OK) {
		return NULL;
	}

	int channel, function;
	int pud = PUD_OFF;
	static char *kwlist[] = {"channel", "function", "pull_up_down", NULL};

	if (!PyArg_ParseTupleAndKeywords(args, kwargs, "ii|i", kwlist, &channel, &function, &pud))
		return NULL;

	if (function != IN && function != OUT && function != PWM)
	{
		PyErr_SetString(_InvalidDirectionException, "Invalid function");
		return NULL;
	}

	if (function == OUT || function == PWM)
	pud = PUD_OFF;

	if (pud != PUD_OFF && pud != PUD_DOWN && pud != PUD_UP)
	{
		PyErr_SetString(_InvalidPullException, "Invalid value for pull_up_down - should be either PUD_OFF, PUD_UP or PUD_DOWN");
		return NULL;
	}

	if (channel < 0 || channel >= GPIO_COUNT)
	{
		PyErr_SetString(_InvalidChannelException, "The GPIO channel is invalid");
		return NULL;
	}

	set_function(channel, function, pud);

	Py_INCREF(Py_None);
	return Py_None;
}

// python function value = input(channel)
static PyObject *py_input(PyObject *self, PyObject *args)
{
	if (module_setup() != SETUP_OK) {
		return NULL;
	}

	int channel;

	if (!PyArg_ParseTuple(args, "i", &channel))
		return NULL;

	if (channel < 0 || channel >= GPIO_COUNT)
	{
		PyErr_SetString(_InvalidChannelException, "The GPIO channel is invalid");
		return NULL;
	}

	if (input(channel))
		Py_RETURN_TRUE;
	else
		Py_RETURN_FALSE;
}

// python function output(channel, value)
static PyObject *py_output(PyObject *self, PyObject *args, PyObject *kwargs)
{
	if (module_setup() != SETUP_OK) {
		return NULL;
	}

	int channel, value;
	static char *kwlist[] = {"channel", "value", NULL};

	if (!PyArg_ParseTupleAndKeywords(args, kwargs, "ii", kwlist, &channel, &value))
		return NULL;

	if (channel < 0 || channel >= GPIO_COUNT)
	{
		PyErr_SetString(_InvalidChannelException, "The GPIO channel is invalid");
		return NULL;
	}

	if (get_function(channel) != OUT)
	{
		PyErr_SetString(_InvalidDirectionException, "The GPIO channel is not an OUTPUT");
		return NULL;
	}

	output(channel, value);

	Py_INCREF(Py_None);
	return Py_None;
}

// python function outputSequence(channel, period, sequence)
static PyObject *py_output_sequence(PyObject *self, PyObject *args, PyObject *kwargs)
{
	if (module_setup() != SETUP_OK) {
		return NULL;
	}

	int channel, period;
	char* sequence;
	static char *kwlist[] = {"channel", "period", "sequence", NULL};

	if (!PyArg_ParseTupleAndKeywords(args, kwargs, "iis", kwlist, &channel, &period, &sequence))
		return NULL;

	if (channel < 0 || channel >= GPIO_COUNT)
	{
		PyErr_SetString(_InvalidChannelException, "The GPIO channel is invalid");
		return NULL;
	}

	if (get_function(channel) != OUT)
	{
		PyErr_SetString(_InvalidDirectionException, "The GPIO channel is not an OUTPUT");
		return NULL;
	}

	outputSequence(channel, period, sequence);

	Py_INCREF(Py_None);
	return Py_None;
}


static PyObject *py_pulseMilli(PyObject *self, PyObject *args, PyObject *kwargs)
{
	if (module_setup() != SETUP_OK) {
		return NULL;
	}

	int channel, function, up, down;
	static char *kwlist[] = {"channel", "up", "down", NULL};

	if (!PyArg_ParseTupleAndKeywords(args, kwargs, "iii", kwlist, &channel, &up, &down))
		return NULL;

	if (channel < 0 || channel >= GPIO_COUNT)
	{
		PyErr_SetString(_InvalidChannelException, "The GPIO channel is invalid");
		return NULL;
	}

	function = get_function(channel);
	if ((function != OUT) && (function != PWM))
	{
		PyErr_SetString(_InvalidDirectionException, "The GPIO channel is not an OUTPUT or PWM");
		return NULL;
	}

	pulseMilli(channel, up, down);

	Py_INCREF(Py_None);
	return Py_None;
}


static PyObject *py_pulseMilliRatio(PyObject *self, PyObject *args, PyObject *kwargs)
{
	if (module_setup() != SETUP_OK) {
		return NULL;
	}

	int channel, function, width;
	float ratio;
	static char *kwlist[] = {"channel", "width", "ratio", NULL};

	if (!PyArg_ParseTupleAndKeywords(args, kwargs, "iif", kwlist, &channel, &width, &ratio))
		return NULL;

	if (channel < 0 || channel >= GPIO_COUNT)
	{
		PyErr_SetString(_InvalidChannelException, "The GPIO channel is invalid");
		return NULL;
	}

	function = get_function(channel);
	if ((function != OUT) && (function != PWM))
	{
		PyErr_SetString(_InvalidDirectionException, "The GPIO channel is not an OUTPUT or PWM");
		return NULL;
	}

	pulseMilliRatio(channel, width, ratio);

	Py_INCREF(Py_None);
	return Py_None;
}


static PyObject *py_pulseMicro(PyObject *self, PyObject *args, PyObject *kwargs)
{
	if (module_setup() != SETUP_OK) {
		return NULL;
	}

	int channel, function, up, down;
	static char *kwlist[] = {"channel", "up", "down", NULL};

	if (!PyArg_ParseTupleAndKeywords(args, kwargs, "iii", kwlist, &channel, &up, &down))
		return NULL;

	if (channel < 0 || channel >= GPIO_COUNT)
	{
		PyErr_SetString(_InvalidChannelException, "The GPIO channel is invalid");
		return NULL;
	}

	function = get_function(channel);
	if ((function != OUT) && (function != PWM))
	{
		PyErr_SetString(_InvalidDirectionException, "The GPIO channel is not an OUTPUT or PWM");
		return NULL;
	}

	pulseMicro(channel, up, down);

	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *py_pulseMicroRatio(PyObject *self, PyObject *args, PyObject *kwargs)
{
	if (module_setup() != SETUP_OK) {
		return NULL;
	}

	int channel, function, width;
	float ratio;
	static char *kwlist[] = {"channel", "width", "ratio", NULL};

	if (!PyArg_ParseTupleAndKeywords(args, kwargs, "iif", kwlist, &channel, &width, &ratio))
		return NULL;

	if (channel < 0 || channel >= GPIO_COUNT)
	{
		PyErr_SetString(_InvalidChannelException, "The GPIO channel is invalid");
		return NULL;
	}

	function = get_function(channel);
	if ((function != OUT) && (function != PWM))
	{
		PyErr_SetString(_InvalidDirectionException, "The GPIO channel is not an OUTPUT or PWM");
		return NULL;
	}

	pulseMicroRatio(channel, width, ratio);

	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *py_pulseAngle(PyObject *self, PyObject *args, PyObject *kwargs)
{
	if (module_setup() != SETUP_OK) {
		return NULL;
	}

	int channel, function;
	float angle;
	static char *kwlist[] = {"channel", "angle", NULL};

	if (!PyArg_ParseTupleAndKeywords(args, kwargs, "if", kwlist, &channel, &angle))
		return NULL;

	if (channel < 0 || channel >= GPIO_COUNT)
	{
		PyErr_SetString(_InvalidChannelException, "The GPIO channel is invalid");
		return NULL;
	}

	function = get_function(channel);
	if ((function != OUT) && (function != PWM))
	{
		PyErr_SetString(_InvalidDirectionException, "The GPIO channel is not an OUTPUT or PWM");
		return NULL;
	}

	pulseAngle(channel, angle);

	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *py_pulseRatio(PyObject *self, PyObject *args, PyObject *kwargs)
{
	if (module_setup() != SETUP_OK) {
		return NULL;
	}

	int channel, function;
	float ratio;
	static char *kwlist[] = {"channel", "ratio", NULL};

	if (!PyArg_ParseTupleAndKeywords(args, kwargs, "if", kwlist, &channel, &ratio))
		return NULL;

	if (channel < 0 || channel >= GPIO_COUNT)
	{
		PyErr_SetString(_InvalidChannelException, "The GPIO channel is invalid");
		return NULL;
	}

	function = get_function(channel);
	if ((function != OUT) && (function != PWM))
	{
		PyErr_SetString(_InvalidDirectionException, "The GPIO channel is not an OUTPUT or PWM");
		return NULL;
	}

	pulseRatio(channel, ratio);

	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *py_pulse(PyObject *self, PyObject *args)
{
	if (module_setup() != SETUP_OK) {
		return NULL;
	}

	int channel;

	if (!PyArg_ParseTuple(args, "i", &channel))
		return NULL;

	if (channel < 0 || channel >= GPIO_COUNT)
	{
		PyErr_SetString(_InvalidChannelException, "The GPIO channel is invalid");
		return NULL;
	}

	pulseRatio(channel, 0.5);
	return Py_None;
}

static PyObject *py_getPulse(PyObject *self, PyObject *args)
{
	if (module_setup() != SETUP_OK) {
		return NULL;
	}

	int channel;
	char str[256];
	struct pulse *p;

	if (!PyArg_ParseTuple(args, "i", &channel))
		return NULL;

	if (channel < 0 || channel >= GPIO_COUNT)
	{
		PyErr_SetString(_InvalidChannelException, "The GPIO channel is invalid");
		return NULL;
	}

	p = getPulse(channel);

	sprintf(str, "%s:%.2f", PWM_MODES[p->type], p->value);
#if PY_MAJOR_VERSION > 2
	return PyUnicode_FromString(str);
#else
	return PyString_FromString(str);
#endif
}

static PyObject *py_enablePWM(PyObject *self, PyObject *args)
{
	if (module_setup() != SETUP_OK) {
		return NULL;
	}

	int channel;

	if (!PyArg_ParseTuple(args, "i", &channel))
		return NULL;

	if (channel < 0 || channel >= GPIO_COUNT)
	{
		PyErr_SetString(_InvalidChannelException, "The GPIO channel is invalid");
		return NULL;
	}

	enablePWM(channel);
	return Py_None;
}

static PyObject *py_disablePWM(PyObject *self, PyObject *args)
{
	if (module_setup() != SETUP_OK) {
		return NULL;
	}

	int channel;

	if (!PyArg_ParseTuple(args, "i", &channel))
		return NULL;

	if (channel < 0 || channel >= GPIO_COUNT)
	{
		PyErr_SetString(_InvalidChannelException, "The GPIO channel is invalid");
		return NULL;
	}

	disablePWM(channel);
	return Py_None;
}



static PyObject *py_isPWMEnabled(PyObject *self, PyObject *args)
{
	if (module_setup() != SETUP_OK) {
		return NULL;
	}

	int channel;

	if (!PyArg_ParseTuple(args, "i", &channel))
		return NULL;

	if (channel < 0 || channel >= GPIO_COUNT)
	{
		PyErr_SetString(_InvalidChannelException, "The GPIO channel is invalid");
		return NULL;
	}

	if (isPWMEnabled(channel))
		Py_RETURN_TRUE;
	else
		Py_RETURN_FALSE;
}

PyMethodDef python_methods[] = {
	{"getFunction", py_get_function, METH_VARARGS, "Return the current GPIO setup (IN, OUT, ALT0)"},
	{"getSetup", py_get_function, METH_VARARGS, "Return the current GPIO setup (IN, OUT, ALT0)"},

	{"getFunctionString", py_get_function_string, METH_VARARGS, "Return the current GPIO setup (IN, OUT, ALT0) as string"},
	{"getSetupString", py_get_function_string, METH_VARARGS, "Return the current GPIO setup (IN, OUT, ALT0) as string"},

	{"setFunction", (PyCFunction)py_set_function, METH_VARARGS | METH_KEYWORDS, "Setup the GPIO channel, direction and (optional) pull/up down control\nchannel   - BCM GPIO number\ndirection - IN or OUT\n[pull_up_down] - PUD_OFF (default), PUD_UP or PUD_DOWN"},
	{"setup", (PyCFunction)py_set_function, METH_VARARGS | METH_KEYWORDS, "Setup the GPIO channel, direction and (optional) pull/up down control\nchannel   - BCM GPIO number\ndirection - IN or OUT\n[pull_up_down] - PUD_OFF (default), PUD_UP or PUD_DOWN"},

	{"input", py_input, METH_VARARGS, "Input from a GPIO channel - Deprecated, use digitalRead instead"},
	{"digitalRead", py_input, METH_VARARGS, "Read a GPIO channel"},

	{"output", (PyCFunction)py_output, METH_VARARGS | METH_KEYWORDS, "Output to a GPIO channel - Deprecated, use digitalWrite instead"},
	{"digitalWrite", (PyCFunction)py_output, METH_VARARGS | METH_KEYWORDS, "Write to a GPIO channel"},

	{"outputSequence", (PyCFunction)py_output_sequence, METH_VARARGS | METH_KEYWORDS, "Output a sequence to a GPIO channel"},

	{"getPulse", py_getPulse, METH_VARARGS, "Read current PWM output"},
	{"pwmRead", py_getPulse, METH_VARARGS, "Read current PWM output"},

	{"pulseMilli", (PyCFunction)py_pulseMilli, METH_VARARGS | METH_KEYWORDS, "Output a PWM to a GPIO channel using milliseconds for both HIGH and LOW state widths"},
	{"pulseMilliRatio", (PyCFunction)py_pulseMilliRatio, METH_VARARGS | METH_KEYWORDS, "Output a PWM to a GPIO channel using millisecond for the total width and a ratio (duty cycle) for the HIGH state width"},
	{"pulseMicro", (PyCFunction)py_pulseMicro, METH_VARARGS | METH_KEYWORDS, "Output a PWM pulse to a GPIO channel using microseconds for both HIGH and LOW state widths"},
	{"pulseMicroRatio", (PyCFunction)py_pulseMicroRatio, METH_VARARGS | METH_KEYWORDS, "Output a PWM to a GPIO channel using microseconds for the total width and a ratio (duty cycle) for the HIGH state width"},

	{"pulseAngle", (PyCFunction)py_pulseAngle, METH_VARARGS | METH_KEYWORDS, "Output a PWM to a GPIO channel using an angle - Deprecated, use pwmWriteAngle instead"},
	{"pwmWriteAngle", (PyCFunction)py_pulseAngle, METH_VARARGS | METH_KEYWORDS, "Output a PWM to a GPIO channel using an angle"},

	{"pulseRatio", (PyCFunction)py_pulseRatio, METH_VARARGS | METH_KEYWORDS, "Output a PWM to a GPIO channel using a ratio (duty cycle) with the default 50Hz signal - Deprecated, use pwmWrite instead"},
	{"pwmWrite", (PyCFunction)py_pulseRatio, METH_VARARGS | METH_KEYWORDS, "Output a PWM to a GPIO channel using a ratio (duty cycle) with the default 50Hz signal"},

	{"pulse", py_pulse, METH_VARARGS, "Output a PWM to a GPIO channel using a 50% ratio (duty cycle) with the default 50Hz signal"},

	{"enablePWM", py_enablePWM, METH_VARARGS, "Enable software PWM loop for a GPIO channel"},
	{"disablePWM", py_disablePWM, METH_VARARGS, "Disable software PWM loop of a GPIO channel"},
	{"isPWMEnabled", py_isPWMEnabled, METH_VARARGS, "Returns software PWM state"},

	{NULL, NULL, 0, NULL}
};

#if PY_MAJOR_VERSION > 2
static struct PyModuleDef python_module = {
	PyModuleDef_HEAD_INIT,
	"_webiopi.GPIO", /* name of module */
	NULL,       /* module documentation, may be NULL */
	-1,         /* size of per-interpreter state of the module,
				  or -1 if the module keeps state in global variables. */
	python_methods
};
#endif

#if PY_MAJOR_VERSION > 2
PyMODINIT_FUNC PyInit_GPIO(void)
#else
PyMODINIT_FUNC initGPIO(void)
#endif
{
	PyObject *module = NULL;
	int revision = -1;

#if PY_MAJOR_VERSION > 2
	if ((module = PyModule_Create(&python_module)) == NULL)
		goto exit;
#else
	if ((module = Py_InitModule("_webiopi.GPIO", python_methods)) == NULL)
		goto exit;
#endif

	_SetupException = PyErr_NewException("_webiopi.GPIO.SetupException", NULL, NULL);
	PyModule_AddObject(module, "SetupException", _SetupException);

	_InvalidDirectionException = PyErr_NewException("_webiopi.GPIO.InvalidDirectionException", NULL, NULL);
	PyModule_AddObject(module, "InvalidDirectionException", _InvalidDirectionException);

	_InvalidChannelException = PyErr_NewException("_webiopi.GPIO.InvalidChannelException", NULL, NULL);
	PyModule_AddObject(module, "InvalidChannelException", _InvalidChannelException);

	_InvalidPullException = PyErr_NewException("_webiopi.GPIO.InvalidPullException", NULL, NULL);
	PyModule_AddObject(module, "InvalidPullException", _InvalidPullException);

	_gpioCount = Py_BuildValue("i", GPIO_COUNT);
	PyModule_AddObject(module, "GPIO_COUNT", _gpioCount);

	_low = Py_BuildValue("i", LOW);
	PyModule_AddObject(module, "LOW", _low);

	_high = Py_BuildValue("i", HIGH);
	PyModule_AddObject(module, "HIGH", _high);

	_in = Py_BuildValue("i", IN);
	PyModule_AddObject(module, "IN", _in);

	_out = Py_BuildValue("i", OUT);
	PyModule_AddObject(module, "OUT", _out);

	_alt0 = Py_BuildValue("i", ALT0);
	PyModule_AddObject(module, "ALT0", _alt0);

	_alt1 = Py_BuildValue("i", ALT1);
	PyModule_AddObject(module, "ALT1", _alt1);

	_alt2 = Py_BuildValue("i", ALT2);
	PyModule_AddObject(module, "ALT2", _alt2);

	_alt3 = Py_BuildValue("i", ALT3);
	PyModule_AddObject(module, "ALT3", _alt3);

	_alt4 = Py_BuildValue("i", ALT4);
	PyModule_AddObject(module, "ALT4", _alt4);

	_alt5 = Py_BuildValue("i", ALT5);
	PyModule_AddObject(module, "ALT5", _alt5);

	_pwm = Py_BuildValue("i", PWM);
	PyModule_AddObject(module, "PWM", _pwm);

	_pud_off = Py_BuildValue("i", PUD_OFF);
	PyModule_AddObject(module, "PUD_OFF", _pud_off);

	_pud_up = Py_BuildValue("i", PUD_UP);
	PyModule_AddObject(module, "PUD_UP", _pud_up);

	_pud_down = Py_BuildValue("i", PUD_DOWN);
	PyModule_AddObject(module, "PUD_DOWN", _pud_down);

	// detect board revision and set up accordingly
	revision = get_rpi_revision();
	if (revision == -1)
	{
		PyErr_SetString(_SetupException, "This module can only be run on a Raspberry Pi!");
#if PY_MAJOR_VERSION > 2
		return NULL;
#else
		return;
#endif
	}

	_board_revision = Py_BuildValue("i", revision);
	PyModule_AddObject(module, "BOARD_REVISION", _board_revision);

	if (Py_AtExit(cleanup) != 0)
	{
		cleanup();
#if PY_MAJOR_VERSION > 2
		return NULL;
#else
		return;
#endif
	}

exit:
#if PY_MAJOR_VERSION > 2
	return module;
#else
	return;
#endif
}
