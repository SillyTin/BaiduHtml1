#include "Strand.h"
using namespace llvm;

void AddInst(strand* st, Instruction* Ins, strand* unuse){
  // errs() << "AddInst\n";
  // errs() << "Instruction:" << *Ins << "\n";


  for(std::vector<Instruction*>::iterator it=st->begin(); it!=st->end();it++){
    if(* it == Ins){
      return;
    }
  }
  st->push_back(Ins);

  for (Use &U : Ins->operands()) {
    Value *v = U.get();
    // errs() << "Value:" << *v << "\n";


    if(isa<User>(v)){
      // errs() << "Def:" << *(dyn_cast<User>(v)) << "\n";
      User* u = dyn_cast<User>(v);

      if(isa<Instruction>(u)){
        // errs() << "Def In:" << *(dyn_cast<Instruction>(u)) << "\n";
        Instruction* In = dyn_cast<Instruction>(u);

        for(std::vector<Instruction*>::iterator it=unuse->begin(); it!=unuse->end();it++){
          // errs() << "for\n";
          if(* it == In){
            // errs() << "if\n";
            it = unuse->erase(it);
            break;
          }
        }
        AddInst(st, In, unuse);
      }
      else{
        // errs() << "Can't cast Instruction\n";
        continue;
      }
    }
    else{
      // errs() << "Can't cast User\n";
      continue;
    }
  }
  return;
}

std::string num2str(int i)
{
  std::stringstream ss;
  ss<<i;
  return ss.str();
}

void Normalize(Instruction* I, int* num){
   for (Use &U : I->operands()){
      Value *v = U.get();
      // errs() << *I << "\n";
      // errs() << v->getName() <<"\n";
      std::string name = v->getName();
      if(name.compare(0,1,"t")){
        v->setName("t"+num2str(*num));
        (*num)++;
      }
      // errs() << v->getName() << "\n";
   }
}

namespace {
  struct Strand : public FunctionPass {
    static char ID;
    Strand() : FunctionPass(ID) {}
    virtual bool runOnFunction(Function& F) {
      errs() << F.getFunction() << "\n";
      errs() << "=============================\n";

      for (BasicBlock &B : F) {
        std::vector<llvm::Instruction *> unuse;
        std::vector<strand> strands;
        for (Instruction &I: B) {
          unuse.push_back(&I);
        }
        while(!unuse.empty()){
          Instruction* I = unuse.back();
          unuse.pop_back();
          strand st;
          // errs() << "new st\n";
          AddInst(&st, I, &unuse);
          strands.push_back(st);
        }

        if(!strands.empty()){
          int num = 0;
          errs() << "--------------Strands-------------\n";
          for(strand s : strands){
            if(!s.empty()){
              strand sr;
              for (std::vector<Instruction*>::iterator rs=s.end()-1; rs!=s.begin()-1;rs--)
              {
                sr.push_back(*rs);
              }
              for(Instruction* I : sr){
                Normalize(I, &num);
              }
              for(Instruction* I : sr){
                errs() << *I <<"\n";
              }
              errs() << "------------------------\n";
            }
          }
        }
      }
      errs() << F.getFunction() << "\n";
      errs() << "=============================\n";

      return false;
    }
  };
}

char Strand::ID = 0;
static RegisterPass<Strand> X("Strand", "Strand Pass",
                             false /* Only looks at CFG */,
                             false /* Analysis Pass */);