/*
 * filter.c
 *
 *  Created on: Apr 7, 2024
 *      Author: Madec
 */

#include "pidFilter.h"
#include "main.h"
#include "quadEncoder.h"
#include "motorCommand.h"
#include <math.h>


//====================================================================
//			PID
//====================================================================

volatile float Kp;
volatile float Kd;
volatile float Ki;
/*volatile*/ uint32_t te_ms;
volatile float LOe_k[3] = {0,0,0};
volatile float LUc_k[2] = {0,0};
volatile float Lcommand;

volatile float ROe_k[3] = {0,0,0};
volatile float RUc_k[2] = {0,0};
volatile float Rcommand;

volatile float debug_tension;

float Ti = 0;
float Td = 0;
float k_alpha = 0;

float b2;
float b1;
float b0;
float a2;
float a1;


void pidFilter_Init(void)
{
	/* PID values */
	Kp = 0.039f;
	Ki = 0.005f;
	Kd = 0.01f;
	te_ms = 5;
	Ti = (Kp/Ki)*(float)te_ms;
	Td = (Kd/Kp)*(float)te_ms;
	Rcommand = 0.0f;
	Lcommand = 0.0f;
	debug_tension = 0.0f;

	/* PID coefficients init */

	b2 = Kp+Kd+Ki;
	b1 = -2*Kd-Kp;
	b0 = Kd;
	a2 = 1;
	a1 = -1;
}

float pidFilter_GetCommandRight(void)
{
	return Rcommand;
}

float pidFilter_GetCommandLeft(void)
{
	return Lcommand;
}

void pidFilter_SetKp(float new_Kp)
{
	Kp = new_Kp;
}

void pidFilter_SetKi(float new_Ki)
{
	Ki = new_Ki;
}

void pidFilter_SetKd(float new_Kd)
{
	Kd = new_Kd;
}

void pidFilter_SetCommandLeft(float new_command)
{
	Lcommand = new_command;
}

void pidFilter_SetCommandRight(float new_command)
{
	Rcommand = new_command;
}

void pidFilter_SetCommandLeftVoltage(float new_voltage)
{
	/* use rated speed of 3000 rpm */
	float new_command = 3000*(new_voltage/24);
	pidFilter_SetCommandLeft(new_command);
}

void pidFilter_SetCommandRightVoltage(float new_voltage)
{
	/* use rated speed of 3000 rpm */
	float new_command = 3000*(new_voltage/24);
	pidFilter_SetCommandRight(new_command);
}

void pidFilter_SetOuterSpeedCommand(float new_speed)
{
	/* 0 <= new_speed <= 3800/15.88 */
	pidFilter_SetCommand(new_speed*15.88f);
}


float pidFilter_ComputeLeft(int16_t output_speed)
{
	/* set k-1 */
	LOe_k[2] = LOe_k[1];
	LOe_k[1] = LOe_k[0];
	LOe_k[0] = Lcommand - (float)output_speed;

	LUc_k[1] = LUc_k[0];

	/* calculate Uc(z) */
	LUc_k[0] = (b2/a2)*LOe_k[0] + (b1/a2)*LOe_k[1] + (b0/a2)*LOe_k[2] - (a1/a2)*LUc_k[1];

	/* no negative voltage */
	if (LUc_k[0] < -24.0f)
	{
		LUc_k[0] = -24.0f;
	}
	else if (LUc_k[0] > 24.0f) /* no voltage superior to 24, both as a command & status*/
	{
		LUc_k[0] = 24.0f;
	}
	/* PWM new duty */
	return LUc_k[0];
}

float pidFilter_ComputeRight(int16_t output_speed)
{
	/* set k-1 */
	ROe_k[2] = ROe_k[1];
	ROe_k[1] = ROe_k[0];
	ROe_k[0] = Rcommand - (float)output_speed;

	RUc_k[1] = RUc_k[0];

	/* calculate Uc(z) */
	RUc_k[0] = (b2/a2)*ROe_k[0] + (b1/a2)*ROe_k[1] + (b0/a2)*ROe_k[2] - (a1/a2)*RUc_k[1];

	/* no negative voltage */
	if (RUc_k[0] < -24.0f)
	{
		RUc_k[0] = -24.0f;
	}
	else if (RUc_k[0] > 24.0f) /* no voltage superior to 24, both as a command & status*/
	{
		RUc_k[0] = 24.0f;
	}
	/* PWM new duty */
	return RUc_k[0];
}
