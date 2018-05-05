using System;
using System.IO;
using System.Collections.Generic;
using System.Collections;
using System.Linq;
using OfficeOpenXml;
using System.Text;
using Microsoft.Office.Interop.Excel;


namespace project
{
	class MainClass
	{
		
		public static double getvalue2(List<double> y, List<double> column1, List<double> column2){
			IEnumerable<double> uniq1 = column1.Distinct ();
			IEnumerable<double> uniq2 = column2.Distinct ();
			List<double> Q = new List<double> ();
			List<double> argnum1 = new List<double> ();
			List<double> argnum2 = new List<double> ();
			foreach (double num1 in uniq1) {
				foreach (double num2 in uniq2) {
					List<int> splitst = new List<int> ();
					List<int> splitnd = new List<int> ();
					List<int> splitrd = new List<int> ();
					List<int> splitth = new List<int> ();
					List<double> Qmax = new List<double> ();

					for (int i = 0; i < column1.Count; i++) {
						if ((column1 [i] <= num1) & (column2 [i] <= num2))
							splitst.Add (i);
						if ((column1 [i] <= num1) & (column2 [i] > num2))
							splitnd.Add (i);
						if ((column1 [i] > num1) & (column2 [i] <= num2))
							splitrd.Add (i);
						if ((column1 [i] > num1) & (column2 [i] > num2))
							splitth.Add (i);
					}
					double sum1 = 0;
					double sum2 = 0;
					double sum3 = 0;
					double sum4 = 0;
					for (int i = 0; i < splitst.Count; i++)
						sum1 += y [splitst [i]];
					for (int i = 0; i < splitnd.Count; i++)
						sum2 += y [splitnd [i]];
					for (int i = 0; i < splitrd.Count; i++)
						sum3 += y [splitrd [i]];
					for (int i = 0; i < splitth.Count; i++)
						sum4 += y [splitth [i]];

					double nu1 = sum1 / splitst.Count;
					double nu2 = sum2 / splitnd.Count;
					double nu3 = sum3 / splitrd.Count;
					double nu4 = sum4 / splitth.Count;
					double nu0 = y.Sum () / column1.Count;

					Qmax.Add (Math.Pow ((nu1 - nu0), 2) * sum1);
					Qmax.Add (Math.Pow ((nu2 - nu0), 2) * sum2);
					Qmax.Add (Math.Pow ((nu3 - nu0), 2) * sum3);
					Qmax.Add (Math.Pow ((nu4 - nu0), 2) * sum4);
					Q.Add (Qmax.Max());
					argnum1.Add (num1);
					argnum2.Add (num2);
				}
			}
			/*
			int bestarg = Q.IndexOf (Q.Max());
			double bestnum1 = argnum1 [bestarg];
			double bestnum2 = argnum2 [bestarg];
			List<int> firstbasket = new List<int> ();
			List<int> secondbasket = new List<int> ();
			List<int> thirdbasket = new List<int> ();
			List<int> fouthbasket = new List<int> ();
			for (int i = 0; i < Mas.Count; i++) {
				if ((column1 [i] <= bestnum1) & (column2 [i] <= bestnum2))
					firstbasket.Add (i);
				if ((column1 [i] <= bestnum1) & (column2 [i] > bestnum2))
					secondbasket.Add (i);
				if ((column1 [i] > bestnum1) & (column2 [i] <= bestnum2))
					thirdbasket.Add (i);
				if ((column1 [i] > bestnum1) & (column2 [i] > bestnum2))
					fouthbasket.Add (i);
			}
			*/
			double bestval = Q.Max ();
			return bestval;
		}

		public static double getvalue(List<double> y, List<double> column){
			IEnumerable<double> uniq1 = column.Distinct ();
			List<double> Q = new List<double> ();
			List<double> argnum1 = new List<double> ();
			//List<double> argnum2 = new List<double> ();
			foreach (double num1 in uniq1) {
				List<int> splitst = new List<int> ();
				List<int> splitnd = new List<int> ();
				//List<int> splitrd = new List<int> ();
				//List<int> splitth = new List<int> ();
				List<double> Qmax = new List<double> ();

				for (int i = 0; i < column.Count; i++) {
					if (column [i] <= num1)
						splitst.Add (i);
					else
						splitnd.Add (i);
				}
				double sum1 = 0;
				double sum2 = 0;
				for (int i = 0; i < splitst.Count; i++)
					sum1 += y [splitst [i]];
				for (int i = 0; i < splitnd.Count; i++)
					sum2 += y [splitnd [i]];

				double nu1 = sum1 / splitst.Count;
				double nu2 = sum2 / splitnd.Count;
				double nu0 = y.Sum () / column.Count;

				Qmax.Add (Math.Pow ((nu1 - nu0), 2) * sum1);
				Qmax.Add (Math.Pow ((nu2 - nu0), 2) * sum2);
				Q.Add (Qmax.Max ());
				argnum1.Add (num1);
			}
			double bestval = Q.Max ();
			return bestval;
		}



		public static void Main (string[] args)
		{
			List<List<double>> Mas = new List<List<double>>() ;
			ExcelPackage xlPackage = new ExcelPackage (new FileInfo ("male.xlsx"));

			var myWorksheet = xlPackage.Workbook.Worksheets.First(); //select sheet 
			var totalRows = myWorksheet.Dimension.End.Row;
			var totalColumns = myWorksheet.Dimension.End.Column;

			var sb = new StringBuilder(); //this is your your data
			for (int rowNum = 1; rowNum <= totalRows; rowNum++) //selet starting row here
			{
				var row = myWorksheet.Cells [rowNum, 1, rowNum, totalColumns].Select (c => c.Value == null ? string.Empty : c.Value.ToString ());
				sb.AppendLine(string.Join(" ", row));
			}
			var ExcelApp = new Microsoft.Office.Interop.Excel.Application();
			var WorkBookExcel  = ExcelApp.Workbooks.Open ("male.txt");
			var WorkSheetExcel = (Microsoft.Office.Interop.Excel.Worksheet)WorkBookExcel.Sheets[1];
			var lastCell = WorkSheetExcel.Cells.SpecialCells(Microsoft.Office.Interop.Excel.XlCellType.xlCellTypeLastCell);
			string[,] list = new string[lastCell.Column, lastCell.Row];

			for(int i=0;i<(int)lastCell.Column;i++)
				for(int j=0;j<(int)lastCell.Row;j++)
					list[i, j] =Convert.ToString( WorkSheetExcel.Cells[j + 1, i + 1]);//считал текст в строку

			StreamReader objReader = new StreamReader("male.txt");
			string sLine="";


			while (sLine != null)
			{
				sLine = objReader.ReadLine();
				if (sLine != null){
					List<double> minimas = new List<double> ();
					string[] row = sLine.Split ();
					for (int i = 0; i < row.Length; i++)
						minimas.Add (Convert.ToDouble (row [i]));
					Mas.Add (minimas);
				}	
			}
			objReader.Close();

			List<double> y = new List<double> ();//change<->shuffle
			List<double> column1 = new List<double> ();
			List<double> column2 = new List<double> ();
			for (int i = 0; i < Mas.Count; i++) {
				y.Add (Mas [i] [1]);//change y<->shuffle
				column1.Add (Mas [i] [3]);
				column2.Add (Mas [i] [4]);
			}
			double y_orig = getvalue2 (y,column1,column2);
			double val_1 = getvalue (y, column1);
			double val_2 = getvalue (y, column2);
			double Q_1_orig = y_orig - val_1;
			double Q_2_orig = y_orig - val_2;
				
			List<double> values1 = new List<double> ();
			List<double> values2 = new List<double> ();
			for (int i = 0; i < 2000; i++) {
				var rnd = new Random ();
				List<double> shuffle_y = y.OrderBy (item => rnd.Next ()).ToList();
				double Q_12 = getvalue2 (shuffle_y,column1,column2);
				double Q_1 = getvalue (shuffle_y,column1);
				double Q_2 = getvalue (shuffle_y,column2);
				values1.Add ((Q_12-Q_1));
				values2.Add ((Q_12-Q_2));	
			}
			List<double> part1 = values1.Where (item => item > Q_1_orig).ToList ();
			List<double> part2 = values1.Where (item => item > Q_2_orig).ToList ();
			Console.WriteLine (part1.Count());
			Console.WriteLine (part2.Count());
		}
			
	}
}
